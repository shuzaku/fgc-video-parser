from flask import Flask, request, jsonify
from downloader import download_youtube_video
from inference import run_inference_on_video
import os

PORT = int(os.environ.get("PORT", 5000))
app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.json
    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "No video_url provided"}), 400
    
    # Step 1: Download the video
    try:
        video_path = download_youtube_video(video_url)
    except Exception as e:
        return jsonify({"error": f"Failed to download video: {str(e)}"}), 500
    
    # Step 2: Run inference on the downloaded video
    try:
        results = run_inference_on_video(video_path)
    except Exception as e:
        return jsonify({"error": f"Inference failed: {str(e)}"}), 500
    
    # Step 3: Return your results (adjust this to your use case)
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True, port=PORT)