# gemini-cli-tutorial
gemini-cli을 사용하여 여러가지 프로젝트를 생성합니다.

## 사용법

이 프로젝트를 실행하기 전에 Python 가상 환경을 설정하는 것이 좋습니다.

1.  **가상 환경 생성 및 활성화:**
    프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 가상 환경을 생성하고 활성화합니다.

    *   **가상 환경 생성:**
        ```bash
        python -m venv venv
        ```

    *   **가상 환경 활성화 (Windows):**
        ```bash
        .\venv\Scripts\activate
        ```

    *   **가상 환경 활성화 (Linux/macOS):**
        ```bash
        source venv/bin/activate
        ```

2.  **필수 라이브러리 설치:**
    가상 환경을 활성화한 후, 다음 명령어를 사용하여 필요한 라이브러리를 설치합니다:
    ```bash
    pip install PyQt5 yt-dlp
    ```

3.  **애플리케이션 실행:**
    모든 설정이 완료되면 다음 명령어를 사용하여 애플리케이션을 실행합니다:
    ```bash
    python app.py
    ```

4.  **YouTube 동영상 다운로드:**
    *   애플리케이션 창이 열리면 'YouTube URL:' 입력란에 다운로드하려는 YouTube 동영상의 URL을 붙여넣습니다.
    *   'Download' 버튼을 클릭합니다.
    *   하단의 로그 창에서 다운로드 진행 상황을 확인할 수 있습니다.