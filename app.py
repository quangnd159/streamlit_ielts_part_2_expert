
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
# eleven_api_key = os.getenv("ELEVEN_API_KEY")

llm = ChatOpenAI(temperature=1.2, model="gpt-3.5-turbo")

# Azure code credit to https://github.com/hipnologo/openai_azure_text2speech

st.set_page_config(page_title="Part 2 Expert", page_icon="🎩")

def get_azure_access_token():
    azure_key = os.environ.get("AZURE_SUBSCRIPTION_KEY")
    try:
        response = requests.post(
            "https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issuetoken",
            headers={
                "Ocp-Apim-Subscription-Key": azure_key
            }
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

    return response.text

def text_to_speech(text, voice_name='en-US-AriaNeural'):
    access_token = get_azure_access_token()

    if not access_token:
        return None

    try:
        response = requests.post(
            "https://southeastasia.tts.speech.microsoft.com/cognitiveservices/v1",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/ssml+xml",
                "X-MICROSOFT-OutputFormat": "riff-24khz-16bit-mono-pcm",
                "User-Agent": "TextToSpeechApp",
            },
            data=f"""
                <speak version='1.0' xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='en-US'>
                <voice name='{voice_name}'>
                <mstts:express-as role="YoungAdultFemale" style="chat">
                    {text}
                </mstts:express-as>
                </voice>
                </speak>
            """,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

    return response.content

def app():
    st.title("IELTS Speaking Part 2 Expert")
    st.sidebar.markdown(
        """
        # Welcome! 👋
        ### 💡 Instructions 

        1. Enter a task card. You can get one [here](https://www.examword.com/ielts-practice/speaking-exam-question)
        2. Enter a specific topic you want to talk about
        3. Hit **Submit**

        You will get a model answer, along with several useful collocations.
        """
    )

    with st.form(key='my_form'):
        card = st.text_area(
            "Enter a task card",
            max_chars=None,
            placeholder="Enter the candidate task card here",
            height=200,
        )
        topic = st.text_input("Enter your chosen topic in reponse to the task card")

        if st.form_submit_button("Submit"):
            with st.spinner('💬 Generating answer...'):
                # Chain 1: Generating an answer
                template = """You are an 18-year-old girl who is attending an English test. 
         Answer the IELTS Speaking Part 2 task card in 180 words using the chosen topic. Use a conversational tone but not too casual. The vocabulary should be that of a high school student.
         Your must not use written English such as "furthermore", "therefore", "overall", and "in conclusion". 
         Here is the task card: {card}. And here's the chosen topic: {topic}"""
                prompt_template = PromptTemplate(input_variables=["card", "topic"], template=template)
                answer_chain = LLMChain(llm=llm, prompt=prompt_template)
                answer_text = answer_chain.run({
                    "card": card,
                    "topic": topic
                })
                # Chain 2: Extract collocations from answer
                template = """Extract 5 good idiomatic expressions from the an IELTS Speaking part 2 answer into bullet points, each accompanied by a definition and an easy and clear example. Here is the answer: {answer_text}"""
                prompt_template = PromptTemplate(input_variables=["answer_text"], template=template)
                collocation_chain = LLMChain(llm=llm, prompt=prompt_template)
                collocations = collocation_chain.run(answer_text)
                st.success(answer_text)
            with st.spinner('🔈 Generating audio and extracting collocations...'):
            # voice_name = st.selectbox("Select a voice:", ['en-US-AriaNeural', 'en-US-GuyNeural', 'en-GB-RyanNeural'])
                answer_audio = text_to_speech(answer_text, 'en-US-AriaNeural')
                with open('answer_audio.wav', 'wb') as f:
                    f.write(answer_audio)
                st.audio('answer_audio.wav')
                st.caption('Download the audio by click on the ⋮ icon on the player.')
                st.header("Collocations")
                st.markdown(collocations)
    st.caption("The text-to-speech service is not free. Please use the app responsibly 🙏")
    st.divider()
    st.write("By [Quang](https://dqnotes.com)")
if __name__ == '__main__':
    app()
