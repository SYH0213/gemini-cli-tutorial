from pytube import YouTube

def download_youtube_video(url):
    try:
        yt = YouTube(url)
        print(f"Downloading: {yt.title}")
        
        # 가장 높은 화질의 스트림 선택
        stream = yt.streams.get_highest_resolution()
        
        # 동영상 다운로드
        stream.download()
        print("Download complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_youtube_video(video_url)
