import streamlit as st
import subprocess
import time
import cv2
import os
st.balloons()


st.title("The CrowdSense....")

st.header("Video uploader")
# Upload video through Streamlit file uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])


if uploaded_file is not None:
    with st.spinner('Wait for it...'):
        time.sleep(5)
    st.success('Done!')
    st.subheader("Uploaded Video:")
    st.write(uploaded_file.name)

    # Display the uploaded video file details
    file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
    st.write(file_details)

    # Display the uploaded video 
    st.video(uploaded_file,start_time=0)


def run_file():
    try:

        st.header("output is::")
        result = subprocess.run(['python', 'PeopleCounter.py'], capture_output=True, text=True)
        st.code(result.stdout, language='python')

        
        time.sleep(5)
        video_file = open(r'C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\output_frame.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes,start_time=0, format="video/mp4")
        
        video_file = open(r'C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\output_mask.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes,start_time=0, format="video/mp4")
        
       
    except subprocess.CalledProcessError as e:
        st.error(f"Error executing PeopleCounter.py: {e}")

# Streamlit app
st.title("Run the file")

# Button to run the Python file
if st.button("Click to Run"):
    run_file()
    time.sleep(10) 