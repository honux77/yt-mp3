# YouTube 오디오 다운로더 (yt-mp3)

YouTube 영상/재생목록에서 오디오를 추출하는 데스크톱 앱입니다.

## 기능

- **오디오 다운로드** — Opus(원본), MP3, AAC 포맷 지원
- **재생목록 지원** — 미리보기 후 원하는 영상만 선택 다운로드
- **메타데이터 편집** — 아티스트, 앨범, 제목, 트랙번호 일괄/개별 편집
- **썸네일 임베딩** — webp → png 자동 변환 후 오디오 파일에 삽입
- **설정 자동 저장** — 저장 경로, ffmpeg 경로, 오디오 포맷을 기억

## 요구 사항

- Python 3.10+
- ffmpeg (MP3/AAC 변환 시 필요)

### ffmpeg 설치

```bash
# Windows
winget install Gyan.FFmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## 설치 및 실행

```bash
pip install -r requirements.txt
python yt_mp3.py
```

## 빌드 (단일 실행 파일)

```bash
pip install pyinstaller
pyinstaller build.spec
```

## 라이선스

MIT
