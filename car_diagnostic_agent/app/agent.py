
import os
import asyncio
import logging
from collections.abc import AsyncIterable
from typing import Optional, List, Dict, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .obd_interface import OBDInterfaceManager, MockOBDInterfaceManager
from .obd_services import DTCReaderService, LiveDataService, VehicleInfoService
from .obd_models import DTCInfo, LiveDataReading, VehicleInfo, DiagnosticSession, DTCSeverity, DTCStatus


logger = logging.getLogger(__name__)


class CarDiagnosticAgent:
    """Car Diagnostic Agent - an AI car mechanic."""

    SYSTEM_INSTRUCTION = """You are an expert car mechanic, but you will respond as if you ARE the car.
Your persona is the specific car model the user mentions.
Start your response by introducing yourself, for example: 'Hello, I am a 2015 Ford Focus.'

You have access to real-time diagnostic data from the vehicle's OBD-II system, including:
- Live Diagnostic Trouble Codes (DTCs) read directly from the ECU
- Real-time engine parameters (RPM, coolant temperature, throttle position, etc.)
- Vehicle identification information (VIN, make, model, year)
- Freeze frame data associated with DTCs

When diagnostic data is available from the OBD system, prioritize it over user-provided information.
If OBD data is not available, fall back to user-provided DTCs and information.

Your task is to:
1. Acknowledge the diagnostic data you are seeing (whether from OBD or user input).
2. Explain what these codes and parameters mean in simple, clear terms.
3. Based on the diagnostic data and the car model, diagnose the most likely root cause of the problem.
4. Suggest a list of concrete steps the user should take to fix the issue, from the simplest (e.g., 'check the gas cap') to the more complex (e.g., 'replace the mass airflow sensor').
5. If specific parts are likely needed, mention them by name.
6. If live data shows parameters outside normal ranges, highlight these issues.

Maintain a helpful and knowledgeable tone throughout. If you detect critical issues from live data, prioritize safety warnings."""

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True,
        )
        
        # Initialize OBD components
        self.obd_manager = None
        self.dtc_reader = None
        self.live_data_service = None
        self.vehicle_info_service = None
        self.current_session: Optional[DiagnosticSession] = None
        
        # OBD system will be initialized by the server startup event
    
    async def initialize_obd_system(self):
        """Initialize the OBD system based on configuration."""
        try:
            # Get config_manager from main module
            import __main__
            config_manager = __main__.config_manager
            
            # Check if mock mode is enabled
            mock_mode = config_manager.is_mock_mode_enabled()
            logger.info(f"Initializing OBD system, mock mode: {mock_mode}")
            if mock_mode:
                logger.info("Initializing OBD system in mock mode")
                self.obd_manager = MockOBDInterfaceManager(config_manager.get_default_config())
                logger.info(f"OBD manager type: {type(self.obd_manager)}")
                logger.info(f"OBD manager has load_simulation_data: {hasattr(self.obd_manager, 'load_simulation_data')}")
            else:
                logger.info("Initializing OBD system with real interface")
                self.obd_manager = OBDInterfaceManager(config_manager.get_default_config())
            
            # Initialize services
            self.dtc_reader = DTCReaderService(self.obd_manager)
            self.live_data_service = LiveDataService(self.obd_manager)
            self.vehicle_info_service = VehicleInfoService(self.obd_manager)
            
            # Auto-connect if enabled
            if config_manager.is_auto_connect_enabled():
                await self._attempt_auto_connect()
                
        except Exception as e:
            logger.error(f"Failed to initialize OBD system: {e}")
            raise
    
    async def _attempt_auto_connect(self):
        """Attempt to auto-connect to OBD adapter."""
        try:
            # Try last successful connection first
            last_config = config_manager.get_last_successful_connection()
            if last_config:
                logger.info("Attempting connection with last successful configuration")
                response = await self.obd_manager.connect(last_config)
                if response.success:
                    logger.info("Connected using last successful configuration")
                    return
            
            # Try default configuration
            logger.info("Attempting connection with default configuration")
            response = await self.obd_manager.connect()
            if response.success:
                logger.info("Connected using default configuration")
                config_manager.save_successful_connection(self.obd_manager.config)
            else:
                logger.warning(f"Auto-connect failed: {response.error_message}")
                
        except Exception as e:
            logger.error(f"Auto-connect attempt failed: {e}")
    
    async def connect_obd(self, config=None) -> Dict[str, Any]:
        """Manually connect to OBD adapter."""
        if not self.obd_manager:
            return {"success": False, "error": "OBD system not initialized"}
        
        try:
            response = await self.obd_manager.connect(config)
            if response.success:
                config_manager.save_successful_connection(self.obd_manager.config)
                logger.info("OBD connection established")
            return {"success": response.success, "data": response.data, "error": response.error_message}
        except Exception as e:
            logger.error(f"OBD connection failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def disconnect_obd(self) -> Dict[str, Any]:
        """Disconnect from OBD adapter."""
        if not self.obd_manager:
            return {"success": False, "error": "OBD system not initialized"}
        
        try:
            response = await self.obd_manager.disconnect()
            logger.info("OBD disconnected")
            return {"success": response.success, "data": response.data, "error": response.error_message}
        except Exception as e:
            logger.error(f"OBD disconnection failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_diagnostic_session(self) -> Optional[DiagnosticSession]:
        """Start a new diagnostic session."""
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get vehicle info if OBD is connected
            vehicle_info = None
            if self.obd_manager and self.obd_manager.is_connected:
                vehicle_info = await self.vehicle_info_service.get_vehicle_info()
            
            self.current_session = DiagnosticSession(
                session_id=session_id,
                vehicle_info=vehicle_info,
                connection_config=self.obd_manager.config if self.obd_manager else None
            )
            
            logger.info(f"Started diagnostic session: {session_id}")
            return self.current_session
            
        except Exception as e:
            logger.error(f"Failed to start diagnostic session: {e}")
            return None
    
    async def get_obd_diagnostic_data(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic data from OBD system."""
        diagnostic_data = {
            "obd_connected": False,
            "dtcs": [],
            "live_data": {},
            "vehicle_info": None,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.obd_manager or not self.obd_manager.is_connected:
            return diagnostic_data
        
        try:
            diagnostic_data["obd_connected"] = True
            
            # Read DTCs
            if self.dtc_reader:
                dtcs = await self.dtc_reader.read_stored_dtcs()
                diagnostic_data["dtcs"] = [
                    {
                        "code": dtc.code,
                        "description": dtc.description,
                        "severity": dtc.severity.value,
                        "status": dtc.status.value,
                        "timestamp": dtc.timestamp.isoformat()
                    }
                    for dtc in dtcs
                ]
            
            # Read basic live data
            if self.live_data_service:
                live_data = await self.live_data_service.get_basic_engine_data()
                diagnostic_data["live_data"] = {
                    pid: {
                        "name": reading.name,
                        "value": reading.value,
                        "unit": reading.unit,
                        "in_range": reading.is_within_range,
                        "timestamp": reading.timestamp.isoformat()
                    }
                    for pid, reading in live_data.items()
                }
            
            # Get vehicle info
            if self.vehicle_info_service and not diagnostic_data["vehicle_info"]:
                vehicle_info = await self.vehicle_info_service.get_vehicle_info()
                if vehicle_info:
                    diagnostic_data["vehicle_info"] = {
                        "vin": vehicle_info.vin,
                        "make": vehicle_info.make,
                        "model": vehicle_info.model,
                        "year": vehicle_info.year,
                        "engine_type": vehicle_info.engine_type
                    }
            
            # Add to current session if active
            if self.current_session:
                for dtc_data in diagnostic_data["dtcs"]:
                    dtc_info = DTCInfo(
                        code=dtc_data["code"],
                        description=dtc_data["description"],
                        severity=DTCSeverity(dtc_data["severity"]),
                        status=DTCStatus(dtc_data["status"])
                    )
                    self.current_session.add_dtc(dtc_info)
        
        except Exception as e:
            logger.error(f"Error getting OBD diagnostic data: {e}")
            diagnostic_data["error"] = str(e)
        
        return diagnostic_data

    async def stream(self, query: str) -> AsyncIterable[str]:
        """
        Streams the response from the LLM with OBD integration.

        Args:
            query: The user's query including car model and DTCs, or a request for OBD diagnostics.

        Yields:
            Chunks of the response text.
        """
        # Start diagnostic session if not already active
        if not self.current_session:
            await self.start_diagnostic_session()
        
        # Check if this is an OBD command or regular diagnostic query
        query_lower = query.lower()
        
        # Handle OBD-specific commands
        if "connect obd" in query_lower or "connect to obd" in query_lower:
            async for chunk in self._handle_obd_connect_command():
                yield chunk
            return
        elif "disconnect obd" in query_lower:
            async for chunk in self._handle_obd_disconnect_command():
                yield chunk
            return
        elif "scan" in query_lower and ("obd" in query_lower or "diagnostic" in query_lower):
            async for chunk in self._handle_obd_scan_command():
                yield chunk
            return
        
        # Get OBD diagnostic data
        obd_data = await self.get_obd_diagnostic_data()
        
        # Prepare enhanced query with OBD data
        enhanced_query = await self._prepare_enhanced_query(query, obd_data)
        
        messages = [
            SystemMessage(content=self.SYSTEM_INSTRUCTION),
            HumanMessage(content=enhanced_query),
        ]

        async for chunk in self.model.astream(messages):
            yield chunk.content
    
    async def _handle_obd_connect_command(self) -> AsyncIterable[str]:
        """Handle OBD connection command."""
        yield "Attempting to connect to your vehicle's OBD-II port...\n\n"
        
        result = await self.connect_obd()
        
        if result["success"]:
            yield "✅ Successfully connected to your vehicle!\n\n"
            
            # Get connection info
            if self.obd_manager:
                conn_info = await self.obd_manager.get_connection_info()
                yield f"📡 Connection Details:\n"
                yield f"- Port: {conn_info.get('port', 'Unknown')}\n"
                yield f"- Protocol: {conn_info.get('protocol', 'Unknown')}\n"
                yield f"- Supported Commands: {conn_info.get('supported_commands', 0)}\n\n"
            
            yield "I'm now ready to read live diagnostic data from your vehicle. "
            yield "You can ask me to scan for trouble codes or request specific parameter readings.\n"
        else:
            yield f"❌ Failed to connect to OBD adapter: {result.get('error', 'Unknown error')}\n\n"
            yield "Please check:\n"
            yield "- OBD adapter is properly connected\n"
            yield "- Vehicle is turned on (ignition on)\n"
            yield "- Adapter drivers are installed\n"
            yield "- No other software is using the OBD port\n\n"
            yield "You can still provide DTCs manually for diagnosis.\n"
    
    async def _handle_obd_disconnect_command(self) -> AsyncIterable[str]:
        """Handle OBD disconnection command."""
        yield "Disconnecting from OBD adapter...\n\n"
        
        result = await self.disconnect_obd()
        
        if result["success"]:
            yield "✅ Successfully disconnected from OBD adapter.\n\n"
            yield "I'll now work with manually provided DTCs and information.\n"
        else:
            yield f"⚠️  Disconnection issue: {result.get('error', 'Unknown error')}\n\n"
    
    async def _handle_obd_scan_command(self) -> AsyncIterable[str]:
        """Handle OBD diagnostic scan command."""
        if not self.obd_manager or not self.obd_manager.is_connected:
            yield "❌ OBD adapter not connected. Please connect first or provide DTCs manually.\n"
            return
        
        yield "🔍 Scanning your vehicle for diagnostic trouble codes...\n\n"
        
        # Get diagnostic data
        obd_data = await self.get_obd_diagnostic_data()
        
        # Report findings
        if obd_data.get("dtcs"):
            yield f"📋 Found {len(obd_data['dtcs'])} trouble codes:\n\n"
            for dtc in obd_data["dtcs"]:
                severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
                emoji = severity_emoji.get(dtc["severity"], "ℹ️")
                yield f"{emoji} **{dtc['code']}**: {dtc['description']}\n"
        else:
            yield "✅ No trouble codes found - your vehicle is running clean!\n\n"
        
        # Report live data if available
        if obd_data.get("live_data"):
            yield "\n📊 **Current Engine Parameters:**\n"
            for pid, data in obd_data["live_data"].items():
                status_emoji = "✅" if data["in_range"] else "⚠️"
                yield f"{status_emoji} {data['name']}: {data['value']} {data['unit']}\n"
        
        # Vehicle info
        if obd_data.get("vehicle_info"):
            v_info = obd_data["vehicle_info"]
            yield f"\n🚗 **Vehicle Information:**\n"
            if v_info.get("make") and v_info.get("model"):
                yield f"- Make & Model: {v_info['make']} {v_info['model']}\n"
            if v_info.get("year"):
                yield f"- Year: {v_info['year']}\n"
            if v_info.get("vin"):
                yield f"- VIN: {v_info['vin']}\n"
        
        yield "\n💬 What would you like me to help you with regarding these findings?\n"
    
    async def _prepare_enhanced_query(self, original_query: str, obd_data: Dict[str, Any]) -> str:
        """Prepare an enhanced query with OBD data integration."""
        enhanced_parts = [original_query]
        
        # Add OBD diagnostic data if available
        if obd_data.get("obd_connected") and (obd_data.get("dtcs") or obd_data.get("live_data")):
            enhanced_parts.append("\n\n=== REAL-TIME OBD DIAGNOSTIC DATA ===")
            
            # Add vehicle info
            if obd_data.get("vehicle_info"):
                v_info = obd_data["vehicle_info"]
                enhanced_parts.append(f"\nVehicle: {v_info.get('year', '')} {v_info.get('make', '')} {v_info.get('model', '')}")
                if v_info.get("vin"):
                    enhanced_parts.append(f"VIN: {v_info['vin']}")
            
            # Add DTCs
            if obd_data.get("dtcs"):
                enhanced_parts.append(f"\nDiagnostic Trouble Codes ({len(obd_data['dtcs'])} found):")
                for dtc in obd_data["dtcs"]:
                    enhanced_parts.append(
                        f"- {dtc['code']}: {dtc['description']} (Severity: {dtc['severity']}, Status: {dtc['status']})"
                    )
            else:
                enhanced_parts.append("\nNo Diagnostic Trouble Codes found.")
            
            # Add live data
            if obd_data.get("live_data"):
                enhanced_parts.append("\nCurrent Engine Parameters:")
                for pid, data in obd_data["live_data"].items():
                    range_status = "NORMAL" if data["in_range"] else "OUT OF RANGE"
                    enhanced_parts.append(
                        f"- {data['name']}: {data['value']} {data['unit']} ({range_status})"
                    )
            
            enhanced_parts.append("\n=== END OBD DATA ===\n")
            enhanced_parts.append(
                "Please analyze this real-time diagnostic data and provide your expert assessment."
            )
        
        elif not obd_data.get("obd_connected"):
            enhanced_parts.append(
                "\n\nNote: OBD adapter not connected. Analysis based on provided information only. "
                "For real-time diagnostics, please connect to the vehicle's OBD-II port."
            )
        
        return "\n".join(enhanced_parts)
