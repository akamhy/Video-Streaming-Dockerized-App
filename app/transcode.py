import subprocess
from typing import Dict


def transcode_to_opus(input_file: str, output_file: str) -> Dict:
    response: Dict = {}
    try:
        # check if input audio is already in Opus codec
        check_command = f"ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=nw=1 {input_file}"
        codec = (
            subprocess.run(check_command, shell=True, stdout=subprocess.PIPE)
            .stdout.strip()
            .decode("utf-8")
        )
        if codec == "opus":
            response["message"] = "Input audio is already in Opus codec"
        else:
            # transcode audio to Opus
            command = f"ffmpeg -i {input_file} -c:a libopus -b:a 64k -vbr on -compression_level 10 {output_file}"
            subprocess.run(command, shell=True, check=True)
            response["message"] = "Audio transcoded to Opus successfully"
    except subprocess.CalledProcessError as e:
        response["error"] = e.output
    return response