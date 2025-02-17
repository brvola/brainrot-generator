import argparse
import json
import os
from pathlib import Path

from controllers.script_controller import ScriptController
from controllers.creation_controller import CreationController
from config.config import CONFIG

def create_project_dir(video_title: str) -> Path:
    base_content_path = Path(CONFIG.get("base_content_path", "content"))
    base_content_path.mkdir(exist_ok=True)
    project_dir = base_content_path / video_title.replace(' ', '_')
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

def save_details(project_path: Path, details: dict):
    details_path = project_path / "details.json"
    with open(details_path, 'w') as details_file:
        json.dump(details, details_file, indent=2, ensure_ascii=False)

def wait_for_confirmation(prompt="Press ENTER when ready..."):
    input(prompt)

def generate_route(args):
    video_title = args.video_title
    project_path = create_project_dir(video_title)
    
    # Get system input from args or fallback to config
    system_input = args.system_input or CONFIG.get("fallbacks", {}).get("system_prompt")
    if not system_input:
        print("No system prompt provided and no fallback found in config.")
        return

    details = {
        "video_title": video_title,
        "system_input": system_input,  # Use the resolved system_input
        "user_input": args.user_input,
        "script_model": CONFIG.get("openai_settings", {}).get("script_model", "gpt-4o"),
        "audio_provider": CONFIG.get("audio_settings", {}).get("provider", "elevenlabs")
    }
    save_details(project_path, details)
    
    script_path = project_path / "script.txt"
    audio_path = project_path / "audio.mp3"
    transcript_path = project_path / "transcript.json"
    
    sc = ScriptController()
    cc = CreationController()
    
    # Generate the script.
    script = sc.generate_script(system_input, args.user_input, details["script_model"], script_path)
    if script is None:
        print("Failed to generate script.")
        return
    
    print(f"Script generated at: {script_path}\n")
    print("Please review and edit the script if needed. Once updated, save the file and then press ENTER to continue.")
    wait_for_confirmation()
    
    with open(script_path, 'r') as f:
        script = f.read()
    
    sc.generate_audio(script, details["audio_provider"], audio_path)
    print(f"Audio generated at: {audio_path}\n")
    
    sc.generate_transcript(str(audio_path), transcript_path)
    print(f"Transcript generated at: {transcript_path}\n")
    
    sc.verify_transcript(str(transcript_path), str(project_path))
    
    cc.create_video_with_project_path(str(project_path))

def transcript_route(args):
    video_title = args.video_title
    project_path = create_project_dir(video_title)

    audio_path = Path(args.audio_path)
    if not audio_path.exists():
        print(f"Provided audio file {audio_path} does not exist.")
        return
    
    details = {
        "video_title": video_title,
    }
    save_details(project_path, details)
    
    project_audio_path = project_path / "audio.mp3"
    if audio_path != project_audio_path:
        import shutil
        shutil.copy(audio_path, project_audio_path)
    
    transcript_path = project_path / "transcript.json"
    
    sc = ScriptController()
    cc = CreationController()
    
    sc.generate_transcript(str(project_audio_path), transcript_path)
    print(f"Transcript generated at: {transcript_path}\n")
    
    cc.create_video_with_project_path(str(project_path))

def parse_args():
    parser = argparse.ArgumentParser(
        description="Video Creation Tool with script generation and transcript-based video assembly"
    )
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')
    
    generate_parser = subparsers.add_parser('generate', help='Generate a video from a generated script.')
    generate_parser.add_argument("--video_title", type=str, required=True, help="Title of the video")
    generate_parser.add_argument("--system_input", type=str, required=False,
                        help="System prompt for script generation. If not provided, the fallback from config will be used.")
    generate_parser.add_argument("--user_input", type=str, required=True,
                        help="User input (e.g. reddit post text) for script generation")
    
    transcript_parser = subparsers.add_parser('transcript', help='Generate video using an existing audio file (transcript generation only).')
    transcript_parser.add_argument("--video_title", type=str, required=True, help="Title of the video")
    transcript_parser.add_argument("--audio_path", type=str, required=True, help="Path to the existing audio file (mp3 format)")
    
    return parser.parse_args()

def main():
    args = parse_args()
    if args.command == 'generate':
        generate_route(args)
    elif args.command == 'transcript':
        transcript_route(args)
    else:
        print("Please specify a valid command ('generate' or 'transcript').")

if __name__ == "__main__":
    main() 