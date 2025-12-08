# 🛡️ Information Security Engineer (정보보안기사)

> **The Definitive Guide for Information Security Engineer Certification & Knowledge Base.**
> 본 저장소는 정보보안기사 자격 취득을 위한 핵심 이론, 실무 기술, 법규 사항을 체계적으로 정리한 아카이브입니다.

![License](https://img.shields.io/badge/license-MIT-green) ![Status](https://img.shields.io/badge/status-Active-blue) ![Exam](https://img.shields.io/badge/Exam-KISA-red)

## 📋 Table of Contents

1. [System Security](#1-system-security-시스템-보안)
2. [Network Security](#2-network-security-네트워크-보안)
3. [Application Security](#3-application-security-애플리케이션-보안)
4. [Information Security General](#4-information-security-general-정보보안-일반)
5. [Management & Laws](#5-management--laws-정보보안-관리-및-법규)

---

## 1. System Security (시스템 보안)

**Objective:** OS(Operating System)의 구조적 취약점을 이해하고 계정, 권한, 로그 관리를 통한 서버 Hardening 수행.

* Account Management:
  * `Root/Admin` 권한 관리 및 Sudoers 설정.
  * 패스워드 정책 (임계치, 복잡도, 유효기간) 및 Shadow 파일 분석.
* Permission & File System:
  * UNIX 파일 권한 (`chmod`, `chown`, `umask`).
  * 특수 권한 보안 위협 (SetUID, SetGID, Sticky Bit) 및 대응.
* System Logs & Forensics:
  * **Linux:** `/var/log/messages`, `auth.log`, `wtmp`, `btmp`, `syslog` 데몬 구조.
  * **Windows:** Event Viewer (Security, System, Application), Audit Policy 설정.
* System Attacks:
  * Buffer Overflow (Stack/Heap based), Race Condition, Format String Attack.

## 2. Network Security (네트워크 보안)

**Objective:** OSI 7 Layer 기반의 프로토콜 취약점 분석 및 보안 장비 운용 능력 배양.



[Image of OSI 7 Layer Model with security protocols at each layer]


* OSI 7 Layer & Protocols:
  * TCP/IP Handshake (3-way, 4-way), UDP 특성.
  * Packet Sniffing (Wireshark, tcpdump) 및 Protocol Anomaly 분석.
* Attacks & Defense:
  * **DoS/DDoS:** SYN Flood, Smurf, Slowloris, UDP Flood 및 대응책(Syncookies 등).
  * **Spoofing:** ARP Spoofing, IP Spoofing, DNS Spoofing.
* Security Appliances:
  * **Firewall:** Packet Filtering vs Stateful Inspection vs ALG.
  * **IDS/IPS:** 오용 탐지(Signature) vs 이상 탐지(Anomaly).
  * **VPN:** IPSec (AH/ESP, Tunnel/Transport Mode), SSL/TLS VPN.

## 3. Application Security (애플리케이션 보안)

**Objective:** 웹 어플리케이션 취약점(OWASP) 대응 및 데이터베이스, 이메일, FTP 보안.

* Web Vulnerabilities (OWASP Top 10):
  * **Injection:** SQL Injection (Union, Error-based, Blind), Command Injection.
  * **Broken Auth:** 세션 하이재킹, 크리덴셜 스터핑.
  * **XSS & CSRF:** Reflected/Stored XSS, CSRF 토큰 검증.
* Secure Coding:
  * 입력값 검증(Input Validation), 에러 처리, 시큐어 코딩 가이드라인.
* Database Security:
  * TDE(Transparent Data Encryption), 접근 제어, 무결성 확보.
* Protocols:
  * HTTP/HTTPS 메커니즘, FTP(Active/Passive), SMTP/POP3/IMAP 보안.

## 4. Information Security General (정보보안 일반)

**Objective:** 암호학의 수학적 원리와 접근 통제 모델, 정보보호의 핵심 원칙 이해.



[Image of CIA Triad Information Security diagram]


* CIA Triad:
  * 기밀성(Confidentiality), 무결성(Integrity), 가용성(Availability).
* Cryptography:
  * **Symmetric:** DES, AES, SEED, ARIA, HIGHT (Block/Stream ciphers).
  * **Asymmetric:** RSA, ECC, ElGamal, Diffie-Hellman Key Exchange.
  * **Hash & Digital Sign:** SHA-256, HMAC, 전자서명(부인방지).
  * **PKI:** 인증서 구조(X.509), CRL, OCSP.
* Access Control:
  * **Models:** DAC (신분 기반), MAC (등급/규칙 기반, BLP/Biba), RBAC (역할 기반).
  * **AAA:** Authentication, Authorization, Accounting.

## 5. Management & Laws (정보보안 관리 및 법규)

**Objective:** ISMS-P 인증 체계 수립, 위험 관리 방법론, 국내외 법규 준수.

* Governance & Risk Management:
  * 위험 분석(Asset -> Threat -> Vulnerability -> Risk).
  * 위험 처리 전략 (회피, 전가, 완화, 수용).
  * BCP (Business Continuity Plan) & DRP (RTO, RPO).
* Compliance (Laws):
  * **개인정보보호법 & 정보통신망법:** 주요 차이점 및 벌칙 조항.
  * **ISMS-P:** 인증 기준(관리체계 수립 및 운영, 보호대책 요구사항, 개인정보 처리 단계별 요구사항).
  * **Electronic Financial Transactions Act:** 전자금융거래법 핵심 사항.

---

## 🛠 Contribution Workflow

1. Create an **Issue** for a specific study topic.

2. Create a **Branch** (`study/topic-name`) and commit your notes.

3. Submit a **Pull Request** and review contents.


### 📥 Auto-Collected Materials (2025-12-08)
- **[OWASP]** OWASP Top 10 (2021) PDF (Saved to: `materials/OWASP_Top_10_Map.png`)
- **[KISA]** KISA 랜섬웨어 대응 가이드 (Saved to: `materials/KISA_Ransomware_Guide_Placeholder.html`)
