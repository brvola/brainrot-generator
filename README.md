# Video Creation Tool

Video Creation Tool is a Dockerized command-line Python application that helps you generate engaging video content from text. The tool handles the entire workflow—from script generation and audio production to transcription and final video assembly with captions and a title overlay.

## Features

- **Script Generation:**  
  Generates a compelling script using OpenAI's Chat API based on your provided text.

- **Audio Generation:**  
  Converts the script to audio using Text-to-Speech (TTS) providers (either OpenAI or ElevenLabs) as configured.

- **Transcript Generation:**  
  Transcribes the generated audio using the Whisper model to produce accurate captions.

- **Video Assembly:**  
  Combines background video footage with caption overlays and a title overlay to create a final shareable video.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/brvola/brainrot-generator.git
   cd brainrot-generator
   ```

2. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project with the following content:

   ```env
   OPENAI_API_KEY=YOUR_OPENAI_KEY
   ELEVENLABS_API_KEY=YOUR_ELEVENLABS_KEY
   ```

   Replace `YOUR_OPENAI_KEY` and `YOUR_ELEVENLABS_KEY` with your actual API keys.

3. **Build and Run with Docker Compose**

   You can build the Docker image and start the container with:

   ```bash
   docker-compose --build
   ```

   Alternatively, if you prefer to run a one-off command without starting a persistent container, use:

   ```bash
   docker-compose run --rm brainrot-creator <command>
   ```

## Usage

The application supports two main routes: **generate** and **transcript**.

### Generate Mode

The **generate** command executes the complete workflow:
1. Generates a script from your input.
2. Prompts you to review and edit the script.
3. Converts the updated script to audio.
4. Generates a transcript of the audio.
5. Assembles the final video with background footage, captions, and a title overlay.

**Example Command:**

```bash
docker-compose run --rm brainrot-creator generate --video_title "My Video Title" --user_input "Your input text here"
```

*Optional:*  
Use `--system_input` if you wish to override the default system prompt (defined in `src/config/config.json`).

### Transcript Mode

The **transcript** command creates a video using an existing audio file by generating a transcript and overlaying captions.

**Example Command:**

```bash
docker-compose run --rm brainrot-creator transcript --video_title "My Video Title" --audio_path "path/to/audio.mp3"
```

## Configuration

All configuration settings are defined in `src/config/config.json`. This file includes settings for:

- **Video Settings:**  
  Video height, title duration, font size, and title position.

- **Audio Settings:**  
  TTS provider settings for both OpenAI and ElevenLabs.

- **Text Clip Settings:**  
  Font, color, stroke, and crossfade duration for generating caption overlays.

- **Whisper Settings:**  
  Model type and device configuration for audio transcription.

- **Fallbacks:**  
  Default values such as minimum/maximum text clip durations and the system prompt for script generation.

Feel free to modify these settings to suit your specific needs.

## Workflow Overview

1. **Script Generation:**  
   Uses OpenAI's API to craft a script based on your input text.
2. **Review & Edit:**  
   You are prompted to review and, if necessary, edit the generated script.
3. **Audio Production:**  
   Converts the final script to audio using the selected TTS provider.
4. **Transcription:**  
   Transcribes the audio to produce caption data.
5. **Video Assembly:**  
   Combines background video footage, text captions, and a title overlay to produce the final video.

## Troubleshooting

- **API Key Errors:**  
  Double-check your `.env` file to ensure that the API keys are correctly set.

- **Missing Dependencies:**  
  The Docker image installs all system dependencies (e.g., FFmpeg, ImageMagick) required for video processing. If running locally, confirm these are installed.

- **Configuration Issues:**  
  If the tool does not behave as expected, review the settings in `src/config/config.json` and adjust as necessary.

## Contributing

Contributions are welcome! If you have ideas for improvements or have found issues, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [OpenAI](https://openai.com/)
- [ElevenLabs](https://elevenlabs.io/)
- [Whisper](https://github.com/openai/whisper)
- [MoviePy](https://zulko.github.io/moviepy/)
