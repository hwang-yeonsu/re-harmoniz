# re:Harmoniz 자율 루프 — 가이드

[`templates/loop.md`](loop.md)의 동반 문서입니다. 자율 루프가 무엇이고, 왜 존재하며,
주장한 대로 도는지 어떻게 검증하고, **실제로 어디서 도는지**, 그리고 시작하는 정확한
명령은 무엇인지 설명합니다. 템플릿 파일 자체는 간결한 계약서이고, 이 문서는 그 긴 설명입니다.
(영문: [`loop.guide.md`](loop.guide.md).)

---

## 무엇인가

0.7.0 릴리즈가 추가한 건 **파일 하나** — `templates/loop.md`입니다. 연구 프로젝트의
`.claude/loop.md`로 복사해 두면, 그 폴더에서 `/loop`을 켤 때마다 Claude Code가 이 파일을
다시 읽어 진화 루프를 **한 스텝씩** 전진시킵니다.

매 스텝은 세 동작입니다:

1. **JUDGE** — `reharm:pushing`이 스코프(frontier 점수, lint 상태, 성숙도 census, 직전
   stagnation 판정)를 **읽기 전용**으로 점검하고 다음 액션을 지목합니다.
2. **ACT** — 추천된 스킬 하나만 실행합니다: `root` / `reharmonization` / `critique` /
   `modal-interchange` / `experiment-design`. 스킬이 원래 사용자에게 넘기던 모든 승인을
   메인 세션이 대신합니다.
3. **RECORD** — 루프 원장(ledger)에 JSONL 한 줄을 추가합니다.

이건 **7번째 스킬이 아닙니다.** 기존 6개 스킬을 네이티브 `/loop` 명령으로 *구동하는*
프로젝트-로컬 템플릿입니다. 플러그인의 스킬 구성은 그대로입니다.

---

## 왜 존재하는가

re:Harmoniz의 6개 스킬은 전부 설계상 **"아무것도 자동으로 결정하지 않는다"** 입니다
(`EVOLUTION.md` §3/§4). 타깃도 사람이 고르고, 판정도 사람이 합니다. 이 수동 규율이
지식 품질을 지키는 헌법입니다.

하지만 무인 운용이 필요할 때가 있습니다(야간 배치, 장기 누적). 그래서 이 템플릿은 그
원칙을 **의도적으로 포기**하되, 그 override를 **스킬이 아니라 프로젝트-로컬 파일**에
격리해 플러그인 코어를 깨끗하게 둡니다. 결과적으로 6개 스킬은 여전히 헌법을 지키고,
override는 *당신이* 파일을 복사해야만 작동합니다. 하는 일은 전부 되돌릴 수 있고
(`deprecate` = 상태 플립, 삭제 아님) 이중 기록(`E####.md` + 원장)되어 사후 감사가
가능합니다.

---

## 한 사이클 — 한 발화, 6 + 1 스텝

발화 한 번에 정확히 이 순서로 한 번 돕니다:

| # | 스텝 | 하는 일 |
|---|------|---------|
| 00 | **LOCK** | `<ledger>.lock`이 있으면 다른 iteration 진행 중 → `STOP("overlap")`. 없으면 생성. |
| 01 | **LOAD** | 원장 꼬리를 읽어 `N`(완료 횟수) 복구. `MAX_ITERS ≠ inf`이고 `N ≥ MAX_ITERS`면 → `STOP("count-reached")`. |
| 02 | **JUDGE** | `/reharm:pushing` 실행. 다음 액션 `R`, 근거, 최신 stagnation 판정을 취함. `R = current` → `STOP("nothing-pending")`; 판정 ∈ `STOP_ON` → `STOP("stagnation:…")`. |
| 03 | **ACT** | `R`에 대해 **정확히 하나**의 액션 수행. 모든 선택은 DECISION POLICY대로 자동. |
| 04 | **RECORD** | 원장에 JSONL 한 줄 추가. 루프의 **유일한** 상태. |
| 05 | **UNLOCK** | `<ledger>.lock` 제거. |
| 06 | **NEXT ↺** | 다음 깨어남을 예약(ScheduleWakeup, 1200–1800초)하거나 **생략해 종료** — 이렇게 `MAX_ITERS`나 정지 사유에서 자기종료한다. |

---

## 정확히 의도대로 도는가

루프의 신뢰성은 하나에 달렸습니다 — 작성된 방식이 네이티브 `/loop`의 *실제* 동작과
맞아야 합니다. 항목별로 맞습니다:

| 네이티브 /loop이 실제로 하는 일 | loop.md가 거기에 맞춘 설계 |
|--------------------------------|----------------------------|
| 맨손 `/loop`은 `.claude/loop.md`를 읽는다. | 템플릿을 바로 그 경로로 복사한다. |
| 발화마다 파일을 **그대로 다시 먹인다** — 이전 대화 기억에 의존하지 않는다. | 상태를 대화가 아니라 **원장 꼬리**(`N` = 완료 횟수)에서 복구한다. 파일은 self-contained. |
| `dynamic` 모드는 예약 깨어남으로 self-pace하고, **깨어남을 생략하면 종료**된다. | step 6(`dynamic`): stop 사유 없으면 같은 `/loop` 입력으로 재예약, 있으면 생략 → 종료. 이로써 `MAX_ITERS`와 정지조건을 강제한다. |
| dynamic 깨어남 지연은 한정적(≈ 1분–1시간)이고 프롬프트 캐시는 ~5분 윈도우다. | 템플릿은 **1200–1800초**를 고른다 — 캐시 윈도우를 넘겨 비용을 줄이고 폴링하지 않는다. |
| 고정 간격 `/loop`(`/loop 6h`)은 **프롬프트가 멈출 수 없는** 시계로 발화하고, `.claude/loop.md`는 어차피 **맨손** `/loop`의 default prompt다. | 그래서 이 템플릿은 **맨손 `/loop` 전용** — 인터벌을 주지 마라. 자기 페이싱(`MAX_ITERS` / `STOP_ON` 강제)은 dynamic `/loop`에서만 작동하며, 고정 간격은 이를 무시하고 `Esc` / 7일 만료까지 돈다. |
| 두 인스턴스가 같은 파일을 동시에 돌릴 수 있다. | step 0 **LOCK**이 두 번째 동시 실행을 `STOP("overlap")`으로 막는다. 스코프당 루프 하나. |

---

## 실행 모델 — 어디서 돌고, 무엇이 깨어 있어야 하나

**가장 중요하고, 가장 오해하기 쉬운 운영 사실입니다.**

Claude Code의 `/loop`은 **로컬이며 세션에 묶입니다** — OS 수준 cron 데몬도 아니고,
클라우드 작업도 아닙니다. 문서 그대로:

> "Tasks only fire while Claude Code is running and idle. Closing the terminal or
> letting the session exit stops them firing."
> (작업은 Claude Code가 실행 중이고 idle일 때만 발화한다. 터미널을 닫거나 세션이
> 종료되면 발화가 멈춘다.)

메커니즘상, 스케줄러는 살아 있는 CLI 프로세스의 이벤트 루프 안에 있습니다 — 매초 만기
작업을 확인하고 **턴 사이**에 발화합니다(응답 도중이 아님). 그래서 "idle"은 *살아서 입력을
기다리는 중*이라는 뜻이지 잠든 게 아닙니다: 터미널을 닫거나, 프로세스가 종료되거나, 머신이
sleep으로 들어가 OS가 프로세스를 suspend하면 아무것도 발화하지 않습니다.

그래서 이 템플릿(맨손 dynamic `/loop`으로 동작)은:

- **Claude Code 세션이 열려 있어야** 합니다(터미널 또는 `claude.ai/code` 세션). 닫으면 루프가 멈춥니다.
- **머신이 켜져 있고 깨어 있어야** 합니다. 루프는 로컬 CLI 프로세스 안에서 돕니다. 닫힌/슬립 상태의 노트북에서는 발화하지 않습니다.
- 반복 `/loop` 작업은 **7일 후 자동 만료**됩니다. `claude --resume` / `--continue`로 만료 전 작업을 복원하고, 새 대화는 이를 비웁니다.

따라서 self-paced 실행도 머신이 깨어 있는 동안만 전진합니다 — 시스템 `cron`이나 클라우드
Routine이 주는 상시 보장이 아닙니다.

### 노트북을 닫아도 도는 무인 실행이 필요하면

다른 메커니즘을 쓰세요 — **이 `/loop` 템플릿이 아닙니다**:

| 메커니즘 | 세션 열려야? | 머신 깨어야? | 실행 위치 | 최소 간격 | 비고 |
|---------|-------------|-------------|-----------|----------|------|
| **`/loop`** (이 템플릿) | **필요** | **필요** | 로컬 CLI 프로세스 | ~1분 | 7일 만료; 템플릿이 겨냥하는 대상 |
| **Routines** (`/schedule`) | 불필요 | **불필요** | Anthropic 클라우드 | 1시간 | 닫힌 노트북에도 동작; 완전 자율(프롬프트 없음); research preview |
| **Desktop scheduled tasks** | 불필요 | 필요 | 로컬 머신 | 1분 | Desktop 앱 + 깨어 있는 머신 필요 |
| **GitHub Actions** (`schedule:`) | 불필요 | 불필요 | CI 인프라 | cron별 | 로컬 머신 전혀 불필요; 레포 CI에서 실행 |

진짜로 "닫은 채 야간 실행"을 원하면 적절한 도구는 **클라우드 Routines**이며,
Anthropic 관리 인프라에서 돕니다. 다만 이 템플릿은 `/loop` 파일이라 그 자체로는
Routine으로 돌지 **않습니다** — 루프 로직을 Routine 프롬프트로 포팅하는 건 별개 작업이고
현재 템플릿 범위 밖입니다.

(`/schedule` 지원 버전 — v2.1.81+ 필요. Routines는 research preview라 제한과 API가 바뀔
수 있음. 출처: [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks.md),
[routines](https://code.claude.com/docs/en/routines.md).)

---

## 안전장치

되돌리기 버튼 없는 자율은 무모합니다. 계약에 넷을 박아 두었습니다:

- **per-scope lock** — `<ledger>.lock`이 스코프당 루프 하나만 허용. 동시 발화는 `STOP("overlap")`으로 빠짐.
- **외부 원장** — 원장은 스코프 **바깥** `<project>/.reharm-loop/`에 둠. `EVOLUTION.md` §8이 스코프 안 상태파일을 금하고, 밖에 두면 `wiki-lint`가 orphan으로 잡지도 않음.
- **되돌릴 수 있는 deprecate** — 노드를 버릴 때도 **상태 플립**일 뿐 삭제가 아님. 루프는 노드의 세대(generation)를 올리지 않음.
- **이중 로깅** — 스킬이 `E####.md`를 쓰고 루프가 원장 한 줄을 추가하므로, 무인 실행도 한 스텝씩 되짚을 수 있음.

---

## 실험 실행 — 3중 AND 게이트

`experiment-design`은 항상 **설계**합니다(`planned` 노드 + `## Handoff` 블록 사전등록).
*실제* 실험 실행은 세 조건이 모두 충족돼야 합니다:

```
RUN_EXPERIMENTS = yes
  AND  runner 진입점 설정됨   (노드  runner:  또는 스코프 CLAUDE.md §6 Toggles)
  AND  코드 워크스페이스 경로 존재 (스코프 CLAUDE.md §2 / §12)
```

하나라도 빠지면 루프는 **DESIGN + handoff에서 멈추고** `gate = "exec-blocked"`를
기록합니다.

**실행은 fire-and-return입니다.** 루프는 실험을 백그라운드(`run_in_background`, 또는 외부 러너
제출)로 띄우고 **기다리지 않습니다** — 기다리면 실행 내내 스코프 lock을 쥐어 다른 모든 iteration을
얼립니다. 노드를 `status: running`으로 넘기고, 시작 시각을 기록하고, iteration을 끝냅니다. 결과는
`.raw/experiments-results/`로 비동기 도착하며, 루프는 raw 결과를 판정하지 않습니다 — 나중
`reharmonization` Phase C가 사전등록 기준으로 import해 노드를 `imported` / `abandoned`로 넘깁니다.

**폴링.** 매 JUDGE가 먼저 `status: running` 노드를 확인하므로, 결과 회수는 평소 진화 작업에 얹혀
갑니다 — 실험은 병렬로 돌고 대개 전용 폴링이 필요 없습니다(평소 1200–1800초). 할 일이 전혀 없을
때만 짧은 폴링으로 전환합니다: 짧은/불명 실험은 **~240초**(5분 캐시 윈도우 안), 긴 실험이면
**1200초+**, **300초는 피함**. 한 번에 실험 하나. 실행이 `EXP_TIMEOUT`을 넘도록 결과가 없으면
노드를 `abandoned`로 두고 `exec-blocked-needs-human`으로 멈춥니다.

---

## dynamic 전용 — cron이 아닌 이유

이 템플릿은 **맨손 `/loop`**(dynamic, self-paced)으로 동작합니다. 고정 간격/cron 호출은
**의도적으로 지원하지 않습니다**:

- 루프는 자기 다음 깨어남을 예약할지 정함으로써 `MAX_ITERS` / `STOP_ON`을 강제하는데, 그
  self-pacing은 **맨손 `/loop`에서만** 작동합니다.
- 고정 간격 `/loop`(`/loop 6h`)은 프롬프트가 **멈출 수 없는** 스케줄러에 페이싱을 넘깁니다 —
  `MAX_ITERS` / `STOP_ON`을 무시하고 `Esc`나 7일 만료까지 돕니다.
- `.claude/loop.md`는 어차피 맨손 `/loop`의 default prompt입니다.

그래서 **설정할 `MODE`도, 줄 인터벌도 없습니다** — 그냥 `/loop`입니다. 고정 벽시계 일정(예:
야간)이나 닫힌 노트북에서도 살아남는 실행이 필요하면, 그건 이 템플릿이 아니라 클라우드
**Routines**(`/schedule`)의 일입니다 — 위 실행 모델 참고.

---

## 사용법

```bash
# 1. 템플릿을 연구 프로젝트(스코프가 사는 곳)로 복사
cp templates/loop.md  /path/to/your-project/.claude/loop.md
```

```text
# 2. CONFIG 블록을 채우고 고정한다.
SCOPE:           /abs/path/to/scope         # .raw/ + wiki/ 포함
MAX_ITERS:       12                          # N | inf
RUN_EXPERIMENTS: no                          # yes면 실제 코드 실행, 위 게이트 적용
SIBLING_SCOPE:   none                        # modal-interchange 도너 스코프
STOP_ON:         reseed, change-strategy
LEDGER:          /abs/your-project/.reharm-loop/scope.jsonl   # 스코프 바깥
```

```bash
# 3. 프로젝트 루트에서 맨손 /loop이 .claude/loop.md를 읽는다
/loop                     # 유일한 호출 — dynamic, MAX_ITERS로 유한 / 자기종료
```

스코프당 루프 하나(lock이 강제). 언제든 `Esc`로 중단. 도는 동안 세션을 열어 두고 머신을
깨워 두세요 — 닫은 채 돌리려면 클라우드 Routines로 전환하세요.

---

## 한계와 주의점

- **노트북 닫으면 안 됨.** `/loop`은 세션이 열려 있고 머신이 깨어 있어야 함. 실행 모델 참고.
- **7일 만료** (반복 작업); `--resume`로 만료 전 작업 복원.
- **맨손 `/loop` 전용 — 인터벌 금지.** 고정 간격 `/loop`은 스스로 못 멈추고(`Esc` / 7일 만료까지) `MAX_ITERS` / `STOP_ON`을 무시함; self-pacing은 dynamic `/loop`이라야 작동.
- **루프당 스코프 하나.** lock이 강제; 두 번째 루프는 다른 스코프를 겨냥.
- **실험은 게이트됨.** 세 조건이 모두 충족되지 않으면 설계 + handoff에서 멈춤 — 의도된 동작.
