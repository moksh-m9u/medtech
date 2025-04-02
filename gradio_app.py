#LINE 11 me GROQ ki API KEY MANUALLY DAALNI HAI FOR RUNNING LOCALLY
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query, generate_doctor_response_text
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

#idhr apni grq ki api key daal do
# Manually set your API key here (do not load from environment)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "add you api key here")

# DO NOT MODIFY the following prompt strings
MULTIMODAL_PROMPT = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

VOICE_ONLY_PROMPT = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            Based solely on the patient's description and voice input (without any image), do you find anything wrong medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Answer as if you are speaking to a real patient. 
            Do not mention image-related observations. Keep your answer concise (max 2 sentences). No preamble, start your answer right away please
            """

with gr.Blocks() as demo:
    gr.Markdown("## AI Doctor Consultation (by a 1st yr student from USAR)")
    
    # -------------------
    # Step 1: Medical History & Patient Information (Poll)
    # -------------------
    with gr.Column(visible=True, elem_id="poll_section") as poll_section:
        gr.Markdown("### Medical History & Patient Information")
        common_conditions = gr.CheckboxGroup(
            choices=["Diabetes", "Hypertension", "Asthma", "Allergy", "Obesity"],
            label="Select common conditions you suffer from"
        )
        other_condition = gr.Textbox(
            label="Other conditions (if any)",
            placeholder="e.g., thyroid issues, anemia"
        )
        issue_type = gr.Radio(
            choices=["Skin", "Hair", "Body Pain", "General", "Other"],
            label="What kind of issue are you experiencing?"
        )
        specific_issue = gr.Textbox(
            label="If 'Other' for issue type, please specify",
            placeholder="e.g., joint pain, eye strain"
        )
        age_input = gr.Number(label="Age", value=30, precision=0)
        gender_input = gr.Radio(
            choices=["Male", "Female", "Other"],
            label="Gender"
        )
        text_input = gr.Textbox(
            label="Enter your query (Optional)", 
            placeholder="Type your question here..."
        )
        proceed_btn = gr.Button("Proceed to Consultation")
        poll_state = gr.State()  # To hold the poll data
    
    # -------------------
    # Step 2: Consultation
    # -------------------
    with gr.Column(visible=False, elem_id="consult_section") as consult_section:
        gr.Markdown("### Consultation")
        conversation_chat = gr.Chatbot(label="Conversation History")  # Conversation history at the top
        
        with gr.Row():
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Patient's Voice (Optional)")
            image_input = gr.Image(type="filepath", label="Patient's Image (Optional)")
        chat_input = gr.Textbox(label="Your Follow-Up Query (Optional)", placeholder="Type your follow-up question here...")
        submit_btn = gr.Button("Submit Consultation")
        
        # Output ordering: transcript, doctor's response, then doctor's voice playback at the end.
        transcript_output = gr.Textbox(label="Transcribed Speech")
        doctor_response_output = gr.Textbox(label="Doctor's Response")
        doctor_voice_output = gr.Audio(label="Doctor's Voice")
        conv_state = gr.State()  # To hold conversation history
    
    def switch_to_consultation(common, other, issue, specific, age, gender, text_query):
        poll_data = {
            "common_conditions": common,
            "other_condition": other,
            "issue_type": issue,
            "specific_issue": specific,
            "age": age,
            "gender": gender,
            "text_query": text_query
        }
        conv_history = []
        return gr.update(visible=False), gr.update(visible=True), poll_data, conv_history

    proceed_btn.click(
        fn=switch_to_consultation,
        inputs=[common_conditions, other_condition, issue_type, specific_issue, age_input, gender_input, text_input],
        outputs=[poll_section, consult_section, poll_state, conv_state]
    )
    
    def process_inputs(audio_filepath, image_filepath, chat_input, poll_data, conv_history):
        transcript = ""
        if audio_filepath:
            transcript = transcribe_with_groq(
                stt_model="whisper-large-v3", 
                audio_filepath=audio_filepath,
                api_key=GROQ_API_KEY
            )
        
        if chat_input and chat_input.strip():
            user_query = chat_input.strip()
        elif transcript.strip():
            user_query = transcript.strip()
        else:
            user_query = poll_data.get("text_query", "").strip()
        
        if not user_query and not image_filepath:
            return "Please provide a query via voice or text.", "", "", conv_history
        
        poll_summary = ""
        if poll_data:
            common = ", ".join(poll_data.get("common_conditions", []))
            other = poll_data.get("other_condition", "").strip()
            issue = poll_data.get("issue_type", "")
            specific = poll_data.get("specific_issue", "").strip()
            age = poll_data.get("age", "")
            gender = poll_data.get("gender", "")
            poll_summary = f"Patient conditions: {common}."
            if other:
                poll_summary += f" Other: {other}."
            poll_summary += f" Issue type: {issue}."
            if specific:
                poll_summary += f" Specific issue: {specific}."
            poll_summary += f" Age: {age}."
            poll_summary += f" Gender: {gender}."
        
        if image_filepath:
            combined_query = MULTIMODAL_PROMPT + " " + poll_summary + " " + user_query
            encoded_img = encode_image(image_filepath)
            doctor_response = analyze_image_with_query(
                query=combined_query,
                encoded_image=encoded_img,
                model="llama-3.2-11b-vision-preview"
            )
        else:
            combined_query = VOICE_ONLY_PROMPT + " " + poll_summary + " " + user_query
            doctor_response = generate_doctor_response_text(
                query=combined_query,
                model="llama-3.2-11b-vision-preview"
            )
        
        doctor_voice_filepath = text_to_speech_with_elevenlabs(
            input_text=doctor_response, 
            output_filepath="final.mp3"
        )
        
        conv_history.append((user_query, doctor_response))
        
        return transcript if transcript else user_query, doctor_response, doctor_voice_filepath, conv_history

    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input, chat_input, poll_state, conv_state],
        outputs=[transcript_output, doctor_response_output, doctor_voice_output, conversation_chat]
    )

demo.launch(debug=True, share=True)
