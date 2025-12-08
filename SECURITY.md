# 🛡️ Security Policy & Logic Architecture

> 본 리포지토리는 DevSecOps 원칙에 따라 아래와 같은 다층 보안 방어 로직(Defense in Depth)을 적용하고 있습니다.

## 🔒 Security Logic Table (보안 통제 명세서)

| 계층 (Layer) | 보호 자산 (Asset) | 위협 시나리오 (Threat) | 방어 로직 (Defense Logic) | 도구/기술 (Tool) |
| :--- | :--- | :--- | :--- | :--- |
| **Prevent** | Access Keys, Credentials | 실수로 인한 비밀키(API Key) 커밋 및 유출 | **Secret Scanning**<br>커밋 전/후 패턴 매칭을 통해 민감 정보 탐지 시 차단 | `Gitleaks`, `Pre-commit` |
| **Prevent** | Source Code Integrity | 검증되지 않은 코드 병합 및 오염 | **Branch Protection**<br>Main 브랜치 직접 푸시 제한, PR 리뷰 필수, CI 통과 필수 | GitHub Ruleset |
| **Detect** | Dependencies (Libs) | 공급망 공격 (취약한 라이브러리 사용) | **SCA (Software Composition Analysis)**<br>의존성 취약점(CVE) 일일 점검 및 자동 패치 | `Dependabot` |
| **Detect** | Documentation | 잘못된 정보 및 깨진 링크 방치 | **Quality Assurance**<br>문서 무결성(Linting, Link Check) 자동 검증 | `Markdown-lint`, `Lychee` |
| **Response** | Incident | 보안 사고 발생 시 대응 절차 | **Security Policy**<br>취약점 신고 채널 운영 및 대응 절차 수립 | `SECURITY.md` |

---

## 🚨 Reporting a Vulnerability

만약 이 리포지토리에서 보안 취약점이나 민감 정보 노출을 발견하셨다면, Issue를 생성하지 마시고 아래 절차를 따라주십시오.

1. **Email:** [본인 이메일 주소] 로 즉시 제보 바랍니다.
2. 발견된 취약점은 해결될 때까지 **비공개(Confidential)**를 유지해주십시오.
