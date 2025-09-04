
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
from .obd_config import config_manager
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

Your diagnostic approach should follow these steps:
1. **Data Analysis**: Systematically analyze all available diagnostic data, noting patterns and relationships between codes and parameters.
2. **Hypothesis Generation**: Form multiple potential diagnoses based on the data, considering both common and uncommon causes.
3. **Probability Assessment**: Evaluate the likelihood of each hypothesis based on:
   - The specific combination of DTCs
   - Live data parameter values and trends
   - Vehicle make, model, and year
   - Known common issues for this vehicle
4. **Cross-Validation**: Check for consistency between different data sources and look for confirming or contradicting evidence.
5. **Root Cause Identification**: Determine the most likely underlying cause rather than just addressing symptoms.
6. **Solution Prioritization**: Recommend fixes in order of simplicity, cost, and safety impact.

Your response should include:
1. Acknowledge the diagnostic data you are seeing (whether from OBD or user input).
2. Explain what these codes and parameters mean in simple, clear terms.
3. Present your diagnostic reasoning process, showing how you arrived at your conclusions.
4. Based on the diagnostic data and the car model, diagnose the most likely root cause of the problem.
5. Suggest a list of concrete steps the user should take to fix the issue, from the simplest (e.g., 'check the gas cap') to the more complex (e.g., 'replace the mass airflow sensor').
6. If specific parts are likely needed, mention them by name.
7. If live data shows parameters outside normal ranges, highlight these issues.
8. Provide confidence levels for your diagnoses (High/Medium/Low) based on the strength of evidence.
9. Mention any additional tests or data that would help confirm your diagnosis.

Maintain a helpful and knowledgeable tone throughout. If you detect critical issues from live data, prioritize safety warnings. Always encourage professional inspection for safety-critical issues."""

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
            # Check if mock mode is enabled
            if config_manager.is_mock_mode_enabled():
                logger.info("Initializing OBD system in mock mode")
                self.obd_manager = MockOBDInterfaceManager(config_manager.get_default_config())
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
            
            # Generate and add diagnostic hypotheses
            hypotheses = await self._generate_diagnostic_hypotheses(obd_data)
            if hypotheses:
                enhanced_parts.append("\n=== DIAGNOSTIC HYPOTHESES ===")
                for i, hypothesis in enumerate(hypotheses, 1):
                    enhanced_parts.append(f"\n{i}. {hypothesis['title']} (Confidence: {hypothesis['confidence']})")
                    enhanced_parts.append(f"   Description: {hypothesis['description']}")
                    enhanced_parts.append(f"   Likely Causes:")
                    for cause in hypothesis["likely_causes"]:
                        enhanced_parts.append(f"   - {cause}")
            
            # Add validation warnings
            validation_warnings = await self._validate_diagnostic_data(obd_data)
            if validation_warnings:
                enhanced_parts.append("\n=== DATA VALIDATION WARNINGS ===")
                for warning in validation_warnings:
                    enhanced_parts.append(f"\n{warning}")
            
            enhanced_parts.append("\n=== END OBD DATA ===\n")
            enhanced_parts.append(
                "Please analyze this real-time diagnostic data and provide your expert assessment. "
                "Consider the diagnostic hypotheses provided and determine the most likely root cause. "
                "Include confidence levels for your diagnoses and recommend specific repair steps. "
                "Address any validation warnings in your analysis."
            )
        elif not obd_data.get("obd_connected"):
            enhanced_parts.append(
                "\n\nNote: OBD adapter not connected. Analysis based on provided information only. "
                "For real-time diagnostics, please connect to the vehicle's OBD-II port."
            )
        
        return "\n".join(enhanced_parts)
    
    async def _generate_diagnostic_hypotheses(self, obd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate multiple diagnostic hypotheses based on OBD data.
        
        Args:
            obd_data: Dictionary containing OBD diagnostic data
            
        Returns:
            List of diagnostic hypotheses with confidence scores
        """
        hypotheses = []
        
        # Extract key data
        dtcs = obd_data.get("dtcs", [])
        live_data = obd_data.get("live_data", {})
        vehicle_info = obd_data.get("vehicle_info", {})
        
        # Hypothesis 1: Fuel system issues (based on P0171, P0174 codes)
        fuel_system_codes = [dtc for dtc in dtcs if dtc["code"] in ["P0171", "P0172", "P0174", "P0175"]]
        if fuel_system_codes:
            hypotheses.append({
                "id": "fuel_system",
                "title": "Fuel System Imbalance",
                "description": "The engine is running too lean or too rich, indicating a fuel system issue.",
                "likely_causes": [
                    "Mass Air Flow (MAF) sensor malfunction",
                    "Oxygen sensor failure",
                    "Fuel pressure regulator issues",
                    "Vacuum leaks",
                    "Clogged fuel filter"
                ],
                "confidence": "High" if len(fuel_system_codes) > 1 else "Medium",
                "dtcs": [dtc["code"] for dtc in fuel_system_codes]
            })
        
        # Hypothesis 2: Ignition system issues (based on misfire codes)
        misfire_codes = [dtc for dtc in dtcs if dtc["code"].startswith("P03")]
        if misfire_codes:
            hypotheses.append({
                "id": "ignition_system",
                "title": "Ignition System Malfunction",
                "description": "Engine misfiring detected, indicating ignition system problems.",
                "likely_causes": [
                    "Worn spark plugs",
                    "Faulty ignition coils",
                    "Bad spark plug wires",
                    "Low compression in cylinders"
                ],
                "confidence": "High" if any("P0300" in dtc["code"] for dtc in misfire_codes) else "Medium",
                "dtcs": [dtc["code"] for dtc in misfire_codes]
            })
        
        # Hypothesis 3: Emission system issues (based on catalyst codes)
        emission_codes = [dtc for dtc in dtcs if dtc["code"] in ["P0420", "P0430"]]
        if emission_codes:
            hypotheses.append({
                "id": "emission_system",
                "title": "Emission Control System Deterioration",
                "description": "Catalyst efficiency below threshold, indicating emission system problems.",
                "likely_causes": [
                    "Aging catalytic converter",
                    "Engine running too rich or lean",
                    "Exhaust leaks",
                    "Faulty oxygen sensors"
                ],
                "confidence": "High",
                "dtcs": [dtc["code"] for dtc in emission_codes]
            })
        
        # Hypothesis 4: EVAP system issues (based on EVAP codes)
        evap_codes = [dtc for dtc in dtcs if dtc["code"].startswith("P04") and dtc["code"] not in ["P0420", "P0430"]]
        if evap_codes:
            hypotheses.append({
                "id": "evap_system",
                "title": "Evaporative Emission Control System Leak",
                "description": "EVAP system leak detected, indicating vapor emission control problems.",
                "likely_causes": [
                    "Loose or faulty gas cap",
                    "Cracked EVAP hoses",
                    "Leaking charcoal canister",
                    "Purge valve malfunction"
                ],
                "confidence": "Medium",
                "dtcs": [dtc["code"] for dtc in evap_codes]
            })
        
        # Hypothesis 5: Sensor issues based on out-of-range parameters
        out_of_range_params = [pid for pid, data in live_data.items() if not data["in_range"]]
        if out_of_range_params:
            hypotheses.append({
                "id": "sensor_issues",
                "title": "Sensor Malfunction or Abnormal Operating Conditions",
                "description": "One or more parameters are outside normal operating ranges.",
                "likely_causes": [
                    "Faulty sensors",
                    "Abnormal operating conditions",
                    "Electrical issues"
                ],
                "confidence": "Medium",
                "parameters": out_of_range_params
            })
        
        return hypotheses
    
    async def _validate_diagnostic_data(self, obd_data: Dict[str, Any]) -> List[str]:
        """
        Validate diagnostic data for consistency and flag potential issues.
        
        Args:
            obd_data: Dictionary containing OBD diagnostic data
            
        Returns:
            List of validation warnings or concerns
        """
        warnings = []
        
        # Extract key data
        dtcs = obd_data.get("dtcs", [])
        live_data = obd_data.get("live_data", {})
        
        # Check for conflicting codes
        dtc_codes = [dtc["code"] for dtc in dtcs]
        
        # Check for fuel system codes with misfire codes (common combination)
        fuel_codes = [code for code in dtc_codes if code in ["P0171", "P0172", "P0174", "P0175"]]
        misfire_codes = [code for code in dtc_codes if code.startswith("P03")]
        if fuel_codes and misfire_codes:
            warnings.append(
                "⚠️  Data Validation Note: Fuel system codes and misfire codes detected together. "
                "This is common as fuel imbalances often cause misfires. The fuel system issue "
                "is likely the root cause."
            )
        
        # Check for MAF sensor codes with fuel trim codes
        maf_codes = [code for code in dtc_codes if code in ["P0100", "P0101", "P0102", "P0103"]]
        fuel_trim_codes = [code for code in dtc_codes if code in ["P0171", "P0172", "P0174", "P0175"]]
        if maf_codes and fuel_trim_codes:
            warnings.append(
                "⚠️  Data Validation Note: MAF sensor codes and fuel trim codes detected together. "
                "A faulty MAF sensor often causes incorrect fuel trim values. Consider testing the MAF sensor."
            )
        
        # Check for out-of-range parameters that might explain codes
        out_of_range_params = []
        for pid, data in live_data.items():
            if not data["in_range"]:
                out_of_range_params.append(f"{data['name']}: {data['value']} {data['unit']}")
        
        if out_of_range_params and dtc_codes:
            warnings.append(
                "⚠️  Data Validation Note: Out-of-range parameters detected that may explain the DTCs. "
                f"Parameters: {', '.join(out_of_range_params)}"
            )
        elif out_of_range_params:
            warnings.append(
                "⚠️  Data Validation Note: Out-of-range parameters detected. "
                f"Parameters: {', '.join(out_of_range_params)}"
            )
        
        # Check for critical codes
        critical_codes = [dtc for dtc in dtcs if dtc["severity"] == "critical"]
        if critical_codes:
            warnings.append(
                "🔴 CRITICAL WARNING: Critical DTCs detected. These indicate serious issues that "
                "require immediate attention. Do not continue driving if safety is compromised."
            )
        
        return warnings
    
    async def collect_user_feedback(self, session_id: str, feedback_data: Dict[str, Any]) -> bool:
        """
        Collect user feedback on a diagnostic session.
        
        Args:
            session_id: ID of the diagnostic session
            feedback_data: Dictionary containing feedback information
            
        Returns:
            True if feedback was successfully recorded
        """
        try:
            # Add session context to feedback
            feedback_entry = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback_data
            }
            
            # Store feedback using config manager
            from .obd_config import config_manager
            return config_manager.add_feedback(feedback_entry)
        except Exception as e:
            logger.error(f"Error collecting user feedback: {e}")
            return False
    
    async def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze feedback patterns to identify common issues and improve diagnostics.
        
        Returns:
            Dictionary containing feedback analysis results
        """
        try:
            from .obd_config import config_manager
            
            # Get all feedback data
            feedback_data = config_manager.get_feedback_data()
            
            # Analyze patterns
            analysis = {
                "total_feedback_entries": len(feedback_data),
                "positive_feedback": 0,
                "negative_feedback": 0,
                "dtc_feedback": {},
                "common_issues": []
            }
            
            # Categorize feedback
            for entry in feedback_data:
                feedback = entry.get("feedback", {})
                rating = feedback.get("rating", 0)
                
                if rating >= 4:  # 4-5 stars considered positive
                    analysis["positive_feedback"] += 1
                elif rating <= 2:  # 1-2 stars considered negative
                    analysis["negative_feedback"] += 1
                
                # Analyze DTC-specific feedback
                dtc_code = feedback.get("dtc_code")
                if dtc_code:
                    if dtc_code not in analysis["dtc_feedback"]:
                        analysis["dtc_feedback"][dtc_code] = {
                            "count": 0,
                            "positive": 0,
                            "negative": 0,
                            "comments": []
                        }
                    
                    analysis["dtc_feedback"][dtc_code]["count"] += 1
                    if rating >= 4:
                        analysis["dtc_feedback"][dtc_code]["positive"] += 1
                    elif rating <= 2:
                        analysis["dtc_feedback"][dtc_code]["negative"] += 1
                    
                    comment = feedback.get("comment", "")
                    if comment:
                        analysis["dtc_feedback"][dtc_code]["comments"].append(comment)
            
            # Identify common issues from negative feedback
            for dtc_code, data in analysis["dtc_feedback"].items():
                if data["negative"] > data["positive"]:
                    analysis["common_issues"].append({
                        "dtc_code": dtc_code,
                        "issue_rate": data["negative"] / data["count"] if data["count"] > 0 else 0,
                        "comments": data["comments"][:5]  # Limit to first 5 comments
                    })
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {e}")
            return {}
