# app/services/intent_table.py
# Central intent → target mapping
# Each route defines:
#   target: "frontend" | "dotnet" | "python_ai" | "rag"
#   action: for frontend navigation or speech
#   path:   backend API endpoint (if needed)
#   autostart: (optional) boolean for FE
#   speech: (optional) spoken feedback

INTENT_ROUTES = {
    # ===== FRONTEND =====
    "start_detection": {
        "target": "frontend",
        "action": "open_object_detection",
        "autostart": True,
        "speech": "Starting object detection."
    },

    "describe_scene": {
        "target": "frontend",
        "action": "open_scene_description",
        "autostart": True,
        "speech": "Describing the scene."
    },

   "read_text": {
    "target": "frontend",
    "action": "open_text_reader",
    "autostart": True,
    "speech": "Abriendo lector de texto.",
    "payload": { "lang": "es-ES" }  
},

    "detect_colors": {
    "target": "frontend",
    "action": "open_color_detection",
    "autostart": True,
    "speech": "Detectando colores con la cámara.",
    "payload": { "k": 5 }            # default number of colors
},

    # ===== .NET  =====
     "get_care_activities_raw": {
        "target": "dotnet",
        "path": "/IMCareActivity/ReadByTime",   
        "action": "show_care_activities_raw",
        "speech": "Fetching your care activities (raw)."
    },
 # ===== RAG (explain raw data using KB) =====
    # .NET → (payload params as query) → RAG explanation → FE
    "get_care_activities_explained": {
        "target": "rag",
        "action": "show_care_activities_explained",
        "speech": "Resumiendo tus actividades de cuidado.",
        "source_path": "/IMCareActivity/ReadByTime",  # .NET endpoint
        "source_method": "GET",
        "lang": "es"
    },
    # ===== Python AI  =====
    

    # ===== RAG  =====
    "faq": {
        "target": "rag",
        "path": "/rag/query",
        "speech": None
    }
}
