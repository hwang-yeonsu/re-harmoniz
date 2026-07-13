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
   `modal-interchange` / `experiment-design` / `ensemble`. 스킬이 원래 사용자에게 넘기던
   모든 승인을 메인 세션이 대신합니다. (단 하나 절대 받지 않는 추천: §13 딥리서치 승격 —
   설계상 수동 전용.)
3. **RECORD** — 루프 원장(ledger)에 JSONL 한 줄을 추가합니다.

이건 **추가 스킬이 아닙니다.** 기존 7개 스킬을 네이티브 `/loop` 명령으로 *구동하는*
프로젝트-로컬 템플릿입니다. 플러그인의 스킬 구성은 그대로입니다.

---

## 왜 존재하는가

re:Harmoniz의 7개 스킬은 전부 설계상 **"아무것도 자동으로 결정하지 않는다"** 입니다
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
| 06 | **NEXT ↺** | dynamic 모드: 다음 깨어남을 예약(ScheduleWakeup, prompt `<<loop.md-dynamic>>`, 1200–1800초)하거나 **생략해 종료**. interval 모드: 계속하려면 아무것도 안 하고(cron이 알아서 재발화), 끝내려면 **루프의 cron 작업을 CronDelete**. 어느 쪽이든 이렇게 `MAX_ITERS`나 정지 사유에서 자기종료한다. |

---

## 정확히 의도대로 도는가

루프의 신뢰성은 하나에 달렸습니다 — 작성된 방식이 네이티브 `/loop`의 *실제* 동작과
맞아야 합니다. 항목별로 맞습니다:

| 네이티브 /loop이 실제로 하는 일 | loop.md가 거기에 맞춘 설계 |
|--------------------------------|----------------------------|
| 프롬프트 없는 `/loop` — bare **또는** 인터벌만(`/loop 2h`) — 은 `.claude/loop.md`를 읽는다. | 템플릿을 바로 그 경로로 복사한다. |
| 발화마다 파일을 **다시 읽는다**(첫 발화 / 편집 후 / compact 직후엔 전문, 그 외엔 짧은 리마인더 + 전문은 문맥에 유지) — 이전 대화 기억에 의존하지 않는다. | 상태를 대화가 아니라 **원장 꼬리**(`N` = 완료 횟수)에서 복구한다. 파일은 self-contained. |
| `dynamic` 모드는 예약 깨어남으로 self-pace하고, **깨어남을 생략하면 종료**된다. | step 6(`dynamic`): stop 사유 없으면 `prompt = <<loop.md-dynamic>>`(런타임이 이 파일로 재확장하는 센티넬 — 문자열 "/loop"이 아님)로 재예약, 있으면 생략 → 종료. 이로써 `MAX_ITERS`와 정지조건을 강제한다. |
| dynamic 깨어남 지연은 한정적(≈ 1분–1시간)이고 프롬프트 캐시는 ~5분 윈도우다. | 템플릿은 **1200–1800초**를 고른다 — 캐시 윈도우를 넘겨 비용을 줄이고 폴링하지 않는다. |
| **인터벌만** 준 `/loop 2h`도 `.claude/loop.md`를 읽는다: `<<loop.md>>` 센티넬을 prompt로 하는 반복 cron을 만들고, 발화마다 디스크에서 재확장한다 — 다만 cron은 작업을 지우기 전까지 계속 발화한다. | 그래서 interval 모드도 **지원**된다: step 6이 루프 자신의 cron 작업을 찾아(CronList) **CronDelete**해서 끝낸다. 기본은 여전히 dynamic — 종료가 fail-safe(재예약을 안 하면 끝)라서다. 인터벌과 함께 *프롬프트*를 주면 안 된다 — `/loop 2h <prompt>`는 loop.md를 아예 건너뛴다. |
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

그래서 이 템플릿(bare `/loop` 또는 인터벌만 준 `/loop 2h`로 동작)은:

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

### 도중 compact는 안전하다 (`/clear`는 아니다)

긴 실행은 컨텍스트 compaction을 **반드시** 만나는데, 루프는 애초에 그걸 견디게 설계돼
있습니다:

- 대기 중인 깨어남 / cron 작업은 대화 컨텍스트가 아니라 **CLI 프로세스**에 삽니다 —
  compaction(자동이든, tick 사이에 직접 친 `/compact`든)은 스케줄을 건드리지 않습니다.
- 런타임은 compaction 때 "loop.md 이미 전달됨" 표시를 리셋하므로, **다음 발화에는 짧은
  리마인더 대신 loop.md 전문이 다시 들어옵니다**.
- 루프 상태는 애초에 대화에 있던 적이 없습니다 — 매 발화가 `N`과 직전 결정을 **원장
  꼬리**에서 복구합니다.

그러니 특별히 할 일이 없습니다: auto-compact가 일어나게 두거나, 루프가 tick 사이에서
쉬는 동안 `/compact`를 치면, 다음 tick은 원장이 가리키는 지점에서 이어집니다.
auto-compact는 **기본으로 켜져 있고**(`autoCompactEnabled` 기본값 true) 매 턴의 쿼리
파이프라인 안에서 돕니다 — 임계치를 넘긴 tick은 모델을 부르기 *전에* 스스로 compact하며,
키보드 앞에 아무도 없어도 됩니다. 꺼져 있지 않은지만 확인하세요(`/config` →
Auto-compact; 환경변수에 `DISABLE_AUTO_COMPACT` 없음). 매 tick마다 compact를 강제하려
하지는 **마세요**: compaction은 손실 있는 요약이고, 루프의 비용 구조가 기대는 프롬프트
캐시 prefix를 매번 무효화합니다 — 임계치 트리거가 맞는 주기입니다.
안전하지 **않은** 건 `/clear`(또는 새 대화 시작)입니다: 예약된 작업 자체가 지워져
루프가 소리 없이 죽습니다 — `/loop`으로 다시 시작하세요.

---

## 안전장치

되돌리기 버튼 없는 자율은 무모합니다. 계약에 여섯을 박아 두었습니다:

- **per-scope lock** — `<ledger>.lock`(iteration 시작 ts 보관)이 스코프당 루프 하나만 허용. 동시 발화는 `STOP("overlap")`으로 빠짐. 모든 stop은 종료 전 UNLOCK하고, ~1h보다 오래된 lock은 죽은 iteration으로 간주해 회수 — 크래시 한 번이 스코프를 데드락시키지 않음.
- **외부 원장** — 원장은 스코프 **바깥** `<project>/.reharm-loop/`에 둠. `EVOLUTION.md` §8이 스코프 안 상태파일을 금하고, 밖에 두면 `wiki-lint`가 orphan으로 잡지도 않음.
- **되돌릴 수 있는 deprecate** — 노드를 버릴 때도 **상태 플립**일 뿐 삭제가 아님. 루프는 노드의 세대(generation)를 올리지 않음.
- **이중 로깅** — 스킬이 `E####.md`를 쓰고 루프가 원장 한 줄(그 iteration이 건드린 노드를 담는 `targets` 필드 포함)을 추가하므로, 무인 실행도 한 스텝씩 되짚을 수 있음.
- **표적 상한** — `MAX_TARGETS`(기본 2)가 무인 reharmonization iteration 하나가 Phase B에서 자동 선택할 노드 수를 제한. 초과 후보는 다음 tick을 기다림 — 작은 iteration이라야 감사 가능함.
- **수동 전용 행은 수동으로** — 딥리서치 승격 추천(`EVOLUTION.md` §13)은 절대 자동 수용하지 않음: 루프는 그 케스케이드 행을 건너뛰고 다음 후보로 넘어감. 승격은 설계상 사람의 결정.

---

## 실험 실행 — 스위치 하나, 사전조건 둘

`experiment-design`은 항상 **설계**합니다(`planned` 노드 + `## Handoff` 블록 사전등록).
*실제* 실험이 실행되느냐는 **당신이 정하는 스위치 하나** — CONFIG의 `RUN_EXPERIMENTS` —
와, 실행 시점에 **루프가 자동으로 확인하는 사전조건 둘**(스코프에 대한 사실이지 판단이
아님)로 결정됩니다:

```
당신이 설정   RUN_EXPERIMENTS = yes            ← 유일한 스위치; no면 코드를 절대 안 돌림
자동 확인     코드 워크스페이스 경로 존재        (스코프 CLAUDE.md §2 / §12)
자동 확인     runner 사용 가능                  (진입점 설정 — 노드  runner:  또는 스코프
                                                CLAUDE.md §6 — 없으면 아래 기본 runner)
```

스위치가 꺼져 있거나 워크스페이스가 없으면 루프는 **DESIGN + handoff에서 멈추고**
`gate = "exec-blocked"`를 기록합니다: `RUN_EXPERIMENTS: no`면 코드를 아예 안 돌립니다.

**기본 runner — 빈 워크스페이스도 돕니다.** 수동 프로토콜은 runner 진입점을 명시적으로
기록하고 절대 추론하지 않습니다(§12); 스코프 템플릿도 *"비워 두면 실험마다 정한다"*고
말합니다. 무인 루프에서 그 빈칸은 곧 확정 `exec-blocked`이므로, 템플릿에 루프 전용
폴백을 두었습니다: 스위치가 켜져 있고 워크스페이스 경로는 있는데 진입점이 없으면, 루프가
**사전등록을 직접 OPERATIONALIZE합니다** — `<워크스페이스>/.reharm-runner/<노드-stem>/`에
자기완결 스크립트를 쓰고, 실행 **전에** 그 경로를 노드의 `runner:`에 기록한 뒤(§12의
감사 규칙 — 기록하지 추론하지 않는다 — 이 그대로 지켜집니다) 백그라운드로 띄웁니다.
결과 보고서는 `.raw/experiments-results/`에 떨어지고 Phase C가 사전등록 기준으로
판정합니다 — 외부 runner와 정확히 같은 경로입니다. goal이 워크스페이스가 줄 수 없는 것
(데이터, 하드웨어, 자격증명, 외부 서비스)을 요구하면 억지로 돌리지 않습니다 — 기존처럼
`exec-blocked`입니다.

**실행은 fire-and-return입니다.** 루프는 실험을 백그라운드(`run_in_background`, 또는 외부 러너
제출)로 띄우고 **기다리지 않습니다** — 기다리면 실행 내내 스코프 lock을 쥐어 다른 모든 iteration을
얼립니다. 노드를 `status: running`으로 넘기고, 시작 시각을 기록하고, iteration을 끝냅니다. 결과는
`.raw/experiments-results/`로 비동기 도착하며, 루프는 raw 결과를 판정하지 않습니다 — 나중
`reharmonization` Phase C가 사전등록 기준으로 import해 노드를 `imported` / `abandoned`로 넘깁니다.

**폴링.** 매 JUDGE가 먼저 `status: running` 노드를 확인하므로, 결과 회수는 평소 진화 작업에 얹혀
갑니다 — 실험은 병렬로 돌고 대개 전용 폴링이 필요 없습니다(평소 1200–1800초). 할 일이 전혀 없을
때만 짧은 폴링으로 전환합니다: 짧은/불명 실험은 **~240초**(5분 캐시 윈도우 안), 긴 실험이면
**1200초+**, **300초는 피함**. (짧은 폴링은 dynamic 모드에서만 가능합니다 — interval 모드는
간격이 고정이라, 도는 실험은 그냥 다음 tick에 다시 확인합니다.) 한 번에 실험 하나. 실행이
`EXP_TIMEOUT`을 넘도록 결과가 없으면 노드를 `abandoned`로 두고 `exec-blocked-needs-human`으로
멈춥니다.

---

## 두 가지 호출 모드 — dynamic(기본) vs interval

템플릿은 `/loop`의 두 형태 어느 쪽으로도 돕니다 — 둘 다 발화마다 `.claude/loop.md`를
다시 읽고, 둘 다 `MAX_ITERS` / `STOP_ON`을 강제합니다. 차이는 **누가 페이싱하느냐**와
**어떻게 끝나느냐**입니다:

| | **Dynamic** — bare `/loop` (권장) | **Interval** — `/loop 2h` (인터벌만) |
|---|---|---|
| 페이싱 | 루프가 매번 지연을 고름 (평소 1200–1800초, 실험 대기 중엔 짧은 폴링) | 고정 간격: 인터벌당 정확히 한 tick |
| 종료 방식 | **Fail-safe**: 다음 깨어남을 재예약하지 않으면 끝 — 잊어도 종료 | **Fail-open**: 루프가 자기 cron 작업을 CronDelete해야 끝 — 지우기를 놓치면 no-op `STOP` tick이 CronDelete로 잡을 지우거나 7일 만료될 때까지 반복 |
| 런타임에 넘기는 것 | `<<loop.md-dynamic>>` 센티넬로 `ScheduleWakeup` | 호출 시점에 만들어지는 `<<loop.md>>` 센티넬의 반복 cron |
| 의존하는 기능 게이트 | loop.md 로딩 **+** dynamic 깨어남 (플래그 둘) | loop.md 로딩만 (플래그 하나) |

루프는 발화 자체의 문구로 모드를 구분합니다 — dynamic tick은 "ScheduleWakeup을 다시
arm하라"고, interval tick은 "반복 cron이 다음 tick을 알아서 발화한다"고 말합니다 —
그러니 여전히 **설정할 `MODE` 필드는 없습니다**; 호출이 유일한 기준입니다.

interval 모드의 규칙 둘: **인터벌만** 주고(`/loop 2h <prompt>`는 loop.md 대신 그 프롬프트를
씁니다), 정지 사유가 명시적 CronDelete로만 발효된다는 걸 받아들이세요. 기본 권장은 여전히
dynamic입니다 — 종료에 아무 행동도 필요 없기 때문입니다.

닫힌 노트북에서도 살아남는 실행이 필요하면 어느 모드도 답이 아닙니다 — 그건 이 템플릿이
아니라 클라우드 **Routines**(`/schedule`)의 일입니다. 위 실행 모델 참고.

---

## 사용법

명령 하나로 끝내는 길: 연구 프로젝트 루트에서 **`/reharm:loop-setup`**을 실행하세요.
스코프를 탐지하고, CONFIG 선택지를 인터뷰로 받고, 실험 게이트를 미리 검증한 뒤, 이
템플릿으로 `.claude/loop.md`를 쓰고, 같은 호출 안에서 네이티브 `/loop`을 시작합니다 —
**손으로 복사할 것은 없습니다**. 아래의 `cp` + CONFIG 수기 작성은 수동 *대안*이지
선행 단계가 아닙니다.

어느 길이든 이 파일의 정체를 알아 두세요: `.claude/loop.md`는 **연구 프로젝트의**
파일이고(플러그인은 설치·업그레이드 어느 쪽에서도 이 파일을 만들거나 건드리지 않습니다 —
override는 계속 opt-in), 이 템플릿의 **그 시점 사본**입니다. 플러그인을 올려도 스스로
갱신되지 않습니다. 업그레이드 후에는 `/reharm:loop-setup`을 다시 돌리세요: 기존 CONFIG를
보여주고, 확인하면 그대로 유지한 채 나머지를 새 템플릿으로 다시 씁니다. 원장은 이 파일의
일부가 아니므로 갱신된 루프는 멈춘 지점에서 그대로 이어지고, 템플릿이 바뀌어도 스코프에는
**마이그레이션이 필요 없습니다**(노드, 원장 포맷, lock, lint 규칙 모두 무변경).

수동으로 하려면 단계별로:

```bash
# 1. 템플릿을 연구 프로젝트(스코프가 사는 곳)로 복사
cp templates/loop.md  /path/to/your-project/.claude/loop.md
```

```text
# 2. CONFIG 블록을 채우고 고정한다.
SCOPE:           /abs/path/to/scope         # .raw/ + wiki/ 포함
MAX_ITERS:       12                          # N | inf
MAX_TARGETS:     2                           # iteration당 Phase B 자동 선택 상한
RUN_EXPERIMENTS: no                          # yes면 실제 코드 실행, 위 게이트 적용
SIBLING_SCOPE:   none                        # modal-interchange 도너 스코프
STOP_ON:         reseed, change-strategy
LEDGER:          /abs/your-project/.reharm-loop/scope.jsonl   # 스코프 바깥
```

```bash
# 3. 프로젝트 루트에서 /loop(bare 또는 인터벌만)이 .claude/loop.md를 읽는다
/loop                     # 권장 — dynamic, MAX_ITERS로 유한 / 자기종료
/loop 2h                  # 지원 — 고정 간격; 자기 cron 작업을 CronDelete해서 종료
```

스코프당 루프 하나(lock이 강제). 일찍 멈추려면 루프에게 중단하라고 말하세요 — 루프가 스스로 명시적으로
종료합니다(깨어남 재예약을 멈추고, 만든 반복 cron 작업이 있으면 CronDelete). 도는 동안 세션을 열어 두고 머신을
깨워 두세요 — 닫은 채 돌리려면 클라우드 Routines로 전환하세요. 도중 compact는 괜찮고
(위 참고), `/clear`는 루프를 죽입니다.

---

## 한계와 주의점

- **기능 게이트 — 먼저 스모크 테스트.** 이 템플릿이 타는 것들이 Claude Code 빌드에 게이팅됨(고정 버전이 아니라 롤아웃 플래그): `/loop`(bare 또는 인터벌만)의 `.claude/loop.md` 읽기, 그리고 — dynamic 모드만 — self-pacing 깨어남(`ScheduleWakeup`). 플래그가 꺼져 있으면 `/loop`이 loop.md를 무시하거나, dynamic 실행이 1회 tick 후 멈춤(깨어남이 조용히 no-op) — `MAX_ITERS`가 발동하지 않음. 야간 실행을 믿기 전 1-tick 스모크 테스트: `/loop` 실행 → 첫 턴이 이 파일(CONFIG + LEDGER)을 실제로 읽고 **다음 깨어남을 arm하는지(dynamic) 또는 반복 cron 작업을 만들었는지(interval)** 확인. Claude Code 2.1.197에서 동작 확인; interval 모드의 loop.md 로딩(`<<loop.md>>` cron 센티넬)은 2.1.207에서 확인.
- **노트북 닫으면 안 됨.** `/loop`은 세션이 열려 있고 머신이 깨어 있어야 함. 실행 모델 참고.
- **7일 만료** (반복 작업); `--resume`로 만료 전 작업 복원.
- **interval 모드: 인터벌만, 종료는 루프 책임.** `/loop 2h <prompt>`는 loop.md를 건너뛰고(프롬프트가 이김), 정지 사유는 루프 자신의 CronDelete를 통해서만 발효됨 — 그 호출을 놓치거나 거부되면 no-op STOP tick이 CronDelete로 잡을 지우거나 7일 만료될 때까지 반복. dynamic 모드에는 두 함정 다 없음.
- **compact ≠ clear.** 도중 `/compact`(그리고 auto-compact)는 안전; `/clear`나 새 대화는 스케줄을 소리 없이 죽임.
- **루프당 스코프 하나.** lock이 강제; 두 번째 루프는 다른 스코프를 겨냥.
- **실험은 게이트됨.** `RUN_EXPERIMENTS: no`이거나 — `yes`라도 runner/워크스페이스 사전조건이 빠지면 — 설계 + handoff에서 멈춤 — 의도된 동작.
