
import os

import replicate
import streamlit as st
from dotenv import load_dotenv
from elevenlabs import generate
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Retrieve API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
eleven_api_key = os.getenv("ELEVEN_API_KEY")

# Initialize an OpenAI language model instance
llm = OpenAI(temperature=0.9)

def generate_story(text):
    """Generate a story using the langchain library and OpenAI's GPT-3 model."""
    # Set up a prompt template for generating stories
    prompt = PromptTemplate(
        input_variables=["text"],
        template=""" 
         You are a fun and seasoned storyteller. Generate a story for me about {text}.
                 """
    )
    # Create a language model chain using the prompt and OpenAI instance
    story = LLMChain(llm=llm, prompt=prompt)
    # Generate the story
    return story.run(text=text)

def generate_audio(text, voice):
    """Convert the generated story to audio using the Eleven Labs API."""
    # Generate audio from the story text and selected voice
    audio = generate(text=text, voice=voice, api_key=eleven_api_key)
    return audio

def generate_images(story_text):
    """Generate images using the story text using the Replicate API."""
    # Generate images using the story text as input
    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={"prompt": story_text}
    )
    return output

def app():
    # Display the title of the web application
    st.title("Story Storm")

    # Create a form to take user input
    with st.form(key='my_form'):
        # Take a text input for story generation
        text = st.text_input(
            "Enter a word to generate a story",
            max_chars=None,
            type="default",
            placeholder="Enter a word to generate a story",
        )
        # Display a list of available voices for audio generation
        options = ["Bella", "Antoni", "Arnold", "Adam", "Domi", "Elli", "Josh", "Rachel", "Sam"]
        voice = st.selectbox("Select a voice", options)

        # Create a submit button for the form
        if st.form_submit_button("Submit"):
            # Show a spinner during story generation
            with st.spinner('Generating story...'):
                # Generate the story and audio
                story_text = generate_story(text)
                audio = generate_audio(story_text, voice)

            # Display the audio player and play the generated audio
            st.audio(audio, format='audio/mp3')
            # Generate and display images related to the story
            images = generate_images(story_text)
            for item in images:
                st.image(item)

    # Show a message if the text or voice input is not provided
    if not text or not voice:
        st.info("Please enter a word and select a voice")

# Run the web application
if __name__ == '__main__':
    app()
