# EmoBook

## 현재 구성

```text
.
|-- clone.wav        # output
|-- clone_2.wav      # output
|-- sample.mp3      # 샘플 목소리
|-- voxcmp_test.py   # 음성 비교 테스트 스크립트 예정 파일
`-- README.md
```

## 개발 상태

- 테스트는 Colab에서 진행되었습니다.

## 예정 작업 예시

`voxcmp_test.py`에는 다음과 같은 기능을 추가할 수 있습니다.

- WAV 파일 로드 및 기본 메타데이터 확인
- 두 음성 샘플의 길이, 샘플레이트, 채널 수 검증
- 음성 임베딩 또는 특징 추출 기반 유사도 비교
- 감정 분류 모델을 활용한 샘플별 감정 추론

## 사용 방법

현재는 오디오 샘플과 테스트 스크립트 골격만 포함되어 있으므로, 기능 구현 후 아래와 같은 방식으로 실행할 수 있도록 확장하는 것을 권장합니다.
```
!pip install -U voxcpm soundfile gradio
```
```powershell
python voxcpm_test.py
```

## 권장 개발 환경

- Python 3.10 이상
- WAV 오디오 처리를 위한 Python 표준 라이브러리 또는 오디오 분석 라이브러리
  - 예: `wave`, `librosa`, `soundfile`, `numpy`

추가 라이브러리를 도입하면 `requirements.txt` 또는 `pyproject.toml`에 의존성을 명시하는 것이 좋습니다.
