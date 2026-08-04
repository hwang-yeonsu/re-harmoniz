# re:Harmoniz

[English](README.md) · **한국어**

[![최신 버전](https://img.shields.io/github/v/release/hwang-yeonsu/re-harmoniz?label=version&sort=semver&color=blue)](https://github.com/hwang-yeonsu/re-harmoniz/releases)

> **결정을 매듭짓는 리서치 루프** — Claude Code 플러그인 (`reharm`).

**re:Harmoniz = re·search(연구) + re·harmoniz·ation(재화성).** *내려야 하는 결정*은 고정해 둔 채, 그 아래를 떠받치는 것 — **주장(claim)과 그 주장이 딛고 선 근거** — 을 세대를 거듭하며 다시 도출합니다. (이름은 음악 용어 *재화성(reharmonization)*에서 왔습니다: 멜로디는 그대로 두고 그 아래 화성만 다시 짠다는 뜻입니다.)

스코프를 열 때 그 스코프가 무슨 결정을 매듭지으려고 존재하는지 먼저 적습니다. 주장은 그 결정 아래 뻗은 **가지**입니다. 리서치는 가지를 키우고, 검증은 가지를 **칩니다**. 아무 결정도 걸려 있지 않은 가지는 내용이 맞든 틀리든 잘라 냅니다. 결정이 딛고 선 가지에는 적대적 반박자 3인이 붙고, 살아남아야 합니다. 진척은 매듭지은 결정 수로 잽니다 — 위키가 얼마나 많이 아는지로 재지 않습니다.

전부 당신 소유의 순수 Markdown입니다. 프로토콜 전체가 파일 하나에 담겨 있습니다: [`EVOLUTION.md`](EVOLUTION.md).

## 그냥 위키와 뭐가 다른가

대부분의 지식 도구 — Zettelkasten vault, Notion, 이른바 'LLM 위키' 노트 저장소 — 는 **축적**합니다. 새로 더한 노트가 다 똑같이 취급되고, 더미는 커지기만 하죠. re:Harmoniz는 **실무 리서치**, 즉 결국 뭔가를 해야 하는 상황을 위해 만들어졌습니다. 그래서 노트 저장소가 못 하는 두 가지를 합니다:

- **노드는 자기 자리를 값으로 치러야 합니다.** 출처는 선언된 결정에 걸리는 지점에서만 주장이 됩니다. 나머지는 출처 페이지에 남아 인용도 검색도 되지만 비용은 0입니다. 더 이상 아무것도 걸리지 않게 된 노드는 `pruned`가 됩니다 — `deprecated`와 별개인 상태입니다. "아무것도 여기에 안 걸려 있다"와 "이건 틀렸다"는 다른 발견이니까요.
- **검증 깊이는 그 노드에 뭐가 걸려 있는지를 따릅니다.** 결정이 뒤집히는 주장에는 반박자 3인이 붙고 2/3 이상 살아남아야 합니다. 뒷받침용 세부 사항에는 렌즈 1개. 열린 결정이 아무것도 딛고 있지 않은 주장에는 하나도 안 붙습니다 — 대신 잘립니다. 엄격함은 뿌리는 게 아니라 겨누는 것입니다.
- **진척은 세대가 아니라 매듭지은 결정입니다.** 세션 평가기는 `decisions_settled`와 `branches_pruned`를 먼저 세고, 세대는 올라가는데 결정이 셋 세션 연속 안 움직이면 `change-strategy`를 냅니다 — 다른 지표로는 전부 건강해 보이는 실패 유형이죠.
- **이견은 기록에 남습니다.** 모순은 당신이 판정하기 전까지 *양쪽* 노드에 살아 있고, 무너진 주장은 삭제되는 대신 deprecated 처리됩니다. 위키가 제 결론을 스스로 방어하는 셈입니다.

바로 그 점이 다릅니다. 이건 노트 저장소가 아니고, 진리 탐구 엔진도 아닙니다. **결정을 향해 달리는 리서치 엔진**입니다. 섞여 있는 단언을 점점 더 잘게 쪼개 봐야 성숙도 숫자만 올라가고 결정은 그대로이며, 깔끔하게 참이라고 말할 수 있을 만큼 잘게 쪼갠 명제는 대개 실무에 쓰기엔 너무 잘게 쪼개진 것입니다.

## 루프

```
  결정 선언            D1: 32-bit Adam을 8-bit로 교체할까?   (open)
      │
      ▼
  가지 씨앗(seed)     ── 출처는 결정이 걸리는 지점에서만 주장이 된다
      │
      ▼
  변이(mutate)        ── 수정, 새 출처 분해, 반대 근거 사냥
      │
      ▼
  가지치기(prune)     ── 열린 결정이 딛고 있지 않은 가지를 잘라 낸다   ─▶ pruned
      │
      ▼
  자연선택            ── 깊이는 역할을 따른다: 하중을 받으면 반박자 3인, 아니면 렌즈 1개
      │
      ├─ 생존 ─▶ 세대 +1, 승급: seed → developing → hardened → evergreen
      └─ 붕괴 ─▶ deprecated (기록은 보존 — 절대 삭제하지 않음)
      │
      ▼
  결정에 답하기        ── 행동할 수 있게 되는 즉시, 인용 가능한 페이지 하나로
```

새 자료나 새 의심이 쌓일 때마다 돌리세요. 자동으로 결정되는 건 없습니다. 표적도 당신이 고르고, 모호한 것도 당신이 판정하고, 무엇을 자를지도 당신이 정합니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `reharm:root` | 진입점. 스코프를 세팅하면서 무슨 결정을 매듭지으려는지 묻고, 그다음 씨앗을 투입합니다. repo URL, 글, 의사코드, 기존 노트, 막연한 아이디어를 던지면 `.raw/`에 안착하고, **그 결정에 걸리는 지점만** `claims/`(전부 1세대로 탄생)가 됩니다. 나머지는 출처 페이지에 남습니다. 여러 출처는 격리된 sub-agent로 fan-out(출처당 하나)되므로, 한 출처의 서술 틀이 다른 출처의 주장으로 새어들지 않습니다. |
| `reharm:reharmonization` | 열린 결정 하나를 놓고 도는 한 번의 진화 세션 — 프로젝트 이름의 유래가 된 스킬입니다: 회고 → 표적(결정을 먼저, 그다음 노드; 당신이 승인) → 변이 + 가지치기 훑기 → 자연선택(하중을 받는 노드는 반박자 3인, 아니면 렌즈 1개, 아무것도 안 걸렸으면 0개) → 기록. |
| `reharm:modal-interchange` | 스코프 간 매시업 — 평행 스코프에서 지식을 빌려와(평행 선법에서 코드를 빌려오듯) 도메인 교차 통찰을 발행합니다. 인용 전용. 각 매쉬업은 원본 상태의 `borrowed:` 스냅샷을 지니므로, 나중에 원본이 바뀌면 조용한 부패 대신 objection으로 드러납니다. |
| `reharm:critique` | 판정 **과 가지치기** — 모호한 백로그(열린 질문, 정체된 노드, 모순, lint 경고)에 가지치기 대기열(열린 결정에 안 걸렸거나 정착된 결정에만 걸린 노드)까지 모아 짧은 인터뷰로 풀어냅니다. 테마가 비슷한 것들은 멀티셀렉트 일괄 triage 한 번으로, 가지치기는 자동 실행 없이 제안만 하며 *결정에 묶기* 선택지를 나란히 줍니다 — 배정이 빈 건 죽은 가지가 아니라 묶는 걸 빠뜨린 경우가 많으니까요. |
| `reharm:pushing` | 방향 잡기(read-only). 스코프가 선언한 결정과 위키 상태를 함께 읽어 다음 수 — 목표 선언, 씨앗 투입, 진화, 판정, 가지치기, 답변, 막힌 근거의 딥리서치 승격 — 를 근거와 함께 추천합니다. 이미 벌어 둔 가치를 실현하거나 이후 세션 비용을 낮추는 일이 일을 늘리는 일보다 앞서도록 순서가 잡혀 있습니다. 아무것도 바꾸지 않고, 결정은 당신 몫입니다. |
| `reharm:experiment-design` | 현장 실험 설계자. `hardened → evergreen` 관문에 막힌 주장 중 **결과가 행동을 바꿀 수 있는 것**에 대해, 그것을 확증하거나 반증할 실험을 **사전 등록**합니다 — 가설, 각 결과에서 *위키 밖* 무엇이 달라지는지 명명하는 `## Decision at stake` 두 줄(결정 게이트 — 아무것도 달라지지 않으면 등록 대신 되돌려보냅니다), 실행 전에 못 박은 CONFIRM/REFUTE 기준, 기록할 조건. 그런 다음 쉬운 말로 정리한 목표를 러너에 넘깁니다 — 직접 설정한 외부 러너(예: `autoresearch`)일 수도 있고, 기본값은 플러그인의 **runner-worker**(노드에 기록해 두었다가 나중에 사용자나 자율 루프가 띄우는 격리 서브에이전트)입니다. 설계·기록만 할 뿐 코드는 절대 실행하지 않습니다. |
| `reharm:ensemble` | 답변 합성 — 루프의 **출구**. 살아남은 것들을 모아 선언된 결정(또는 스코프의 중심 질문)에 답하는 `deliverables/` 페이지 하나를 만듭니다. 실무자가 그것만 읽고 움직일 수 있는 세 줄 요지로 시작하고, 하중을 받는 모든 문장이 (status · confidence · generation) 스냅샷과 함께 노드를 인용하고, 가장 약한 하중 주장이 신뢰도 하한을 정하며, 남은 유의점은 기록에 남습니다. **결정을 내릴 수 있게 되는 즉시** 돌리세요 — 센서스가 그럴듯해질 때까지 기다리는 게 아닙니다. 같은 파일을 제자리에서 갱신할 뿐, 노드 상태는 절대 바꾸지 않습니다. |

> **뭘 돌려야 할지 모르겠다면?** [`docs/SKILLS.ko.md`](docs/SKILLS.ko.md)가 상황별로 친절하게 안내합니다 — *"이걸 하고 싶다 → 이걸 돌려라"* — 각 스킬이 무엇을 하고 무엇은 건드리지 않는지까지. (아니면 그냥 `reharm:pushing`을 돌리면 다음 수를 짚어 줍니다.)

## 사용 시나리오

**기법 도입 여부 결정.** *"이 옵티마이저로 갈아탈까?"*에 답해야 합니다 — `D1`으로 선언하고, 논문 몇 편과 레퍼런스 repo를 `reharm:root`하세요. D1을 뒤집을 발견만 주장이 되고 나머지는 출처 페이지에 남습니다. 몇 주 뒤 새 결과가 그중 하나를 반박하면 `reharm:reharmonization`을 돌리세요. 반박자들이 양쪽을 시험하고, 진 쪽은 *이유와 함께 기록에 남은 채* deprecated 되며, 살아남은 쪽은 세대를 얻고 이제 독립 출처 2개를 인용합니다. D1에 답할 수 있게 되면 `reharm:ensemble`이 실제로 보고 움직일 페이지를 씁니다.

**스스로 방어하는 문헌 리뷰.** 리뷰가 어떤 결정에 쓰일지 먼저 선언하고, 그 결정을 기준으로 논문을 원자화합니다. 논문 사이의 모순은 당신이 `reharm:critique`에서 정리하기 전까지 *양쪽* 노드에 명시된 채 남습니다. `index.md`의 결정 표가 각 결정이 어디까지 왔는지 보여 주고, 성숙도 통계가 무엇이 단단하고(hardened/evergreen) 무엇이 아직 추측인지(seed)를 한눈에 보여 줍니다.

**경쟁 / 시장 분석.** 벤더 문서, 벤치마크, 현장 보고를 씨앗으로 넣습니다. 적대적 검증이 독립적 뒷받침 없는 마케팅 주장을 걸러 내고, 근거 렌즈를 통과한 단언만 단단해집니다. 나중에 그 주장을 확인하거나 뒤엎는 실사용 결과는 `## Field Evidence` 아래에 덧붙습니다.

**두 연구 트랙 연결.** 스코프가 둘 생기면 — 가령 하나는 *학습*, 하나는 *서빙* — `reharm:modal-interchange`가 한쪽의 미해결 문제를 다른 쪽 메커니즘이 답하는 지점을 찾아냅니다. 그리고 양쪽 원본을 함께 인용하는(단일 진실 공급원) 도메인 교차 통찰을 발행합니다.

**한동안 놔뒀던 스코프로 돌아왔을 때.** 몇 주 만에 스코프를 다시 열었는데 어디까지 했는지 기억나지 않습니다. `reharm:pushing`이 결정 블록, 성숙도 통계, 결정별 frontier 점수, 가지치기 대기열, 열린 모순, 직전 세션의 stagnation 판정을 읽고 다음 수를 짚어 줍니다 — *이제 답할 수 있는 결정에 답하기*(`ensemble`), *죽은 가지 치기*(`critique`), *frontier 노드 진화*(`reharmonization`), *새 자료 씨앗 투입*(`root`) — 각각의 근거와 함께. read-only라서 가리키기만 할 뿐, 결정과 실행은 당신이 합니다.

**바쁜데 안 나아가는 스코프 잡아내기.** 여섯 세션이 지났고 세대는 올라가고 lint는 깨끗하고 생존율도 높은데, 결정은 하나도 안 움직였습니다. 세션 평가기가 이 패턴을 직접 세서 `change-strategy`를 내고, `pushing`은 위키가 아무도 안 기다리는 걸 단단하게 만들고 있다고 그대로 말해 줍니다. 다른 모든 지표가 건강해 보이기 때문에 이 지표를 따로 세는 겁니다.

<details>
<summary><b>전체 워크스루 — 한 주제로 7개 스킬 전부 거치기</b></summary>

스코프는 `Research_optimizers`(학습 단계 최적화)이고, 추론용 평행 스코프 `Research_serving`이 이미 존재합니다.

**⓪ 결정 선언** — 리서치를 시작하기 전에, 스코프 `CLAUDE.md`가 이 스코프의 용도를 말해 둡니다:

```markdown
### Goal & Open Decisions

**Goal:** 모델 품질을 잃지 않으면서 학습 파이프라인의 메모리 예산을 줄인다

| ID | Decision to settle | Status |
|---|---|---|
| D1 | 학습 설정을 8-bit Adam으로 바꿀까? | open |
```

D1이 무엇이 *아닌지* 보세요. *"8-bit Adam이 32-bit만큼 좋은가?"*가 아닙니다. 그건 세상에 관한 질문이죠. D1은 하거나 안 하거나 하는 일이고, 이후 모든 단계가 여기에 맞춰 재어집니다.

**① 씨앗 투입 — `reharm:root`**

```bash
cd 01_Projects/Project_A/Research_optimizers
/reharm:root https://github.com/bitsandbytes-foundation/bitsandbytes
/reharm:root "논문: 8-bit Optimizers via Block-wise Quantization (Dettmers et al., 2022)"
```

repo 덤프와 논문이 `.raw/`에 안착하고 각각 `sources/` 요약이 생깁니다. 논문은 단언을 스무 개쯤 하는데 **그중 둘이 D1에 걸립니다.** 그래서 둘만 주장이 됩니다 — `claims/8bit-adam-matches-32bit-quality.md`와 `claims/stable-embedding-required-for-8bit.md`가 `seed · generation 1 · confidence low · serves: ["D1"]`로 태어납니다. 나머지 열여덟 — 블록 단위 양자화 내부 동작, 벤치마크 표, 관련 연구 정리 — 는 출처 페이지에 남아 필요할 때 인용되고 비용은 0입니다. 각 실행은 **격리된 sub-agent** 안에서 원자화하므로, 여러 출처를 한꺼번에 넣어도 한쪽의 서술 틀이 다른 쪽으로 새어들지 않습니다.

**② 첫 진화 — `reharm:reharmonization` (`E0001.md` 작성)**

Phase B는 D1(유일한 열린 결정)을 고른 다음 *그 결정 안에서* frontier를 요청합니다 — `boundary-score.py --serves D1` — 그렇게 올라온 새 노드를 당신이 승인합니다. Phase C는 결정 앵글을 먼저 잡고 웹에서 반대 근거를 찾아 나섭니다. Phase D는 이 주장이 뒤집히면 D1도 뒤집히므로 **전체 깊이**로 판정합니다: 반박자 3인 — *일관성 · 근거 · 재현성* — 을 돌리고, 재현성 렌즈가 반례(*안정적 임베딩 레이어 없이는 학습이 발산한다*)를 들이밀지만 **3 중 2가 생존**합니다.

→ `generation → 2`, `seed → developing`, `confidence medium`. 반례는 주장의 `## Objections & Limits`로 흡수되고, `E0001.md`가 세 판정을 기록하며, `index.md`와 `hot.md`가 갱신됩니다. *아직 `hardened`는 아닙니다 — 그 관문을 넘으려면 **독립** 출처가 하나 더 필요합니다.*

**③ 둘째 진화 — `reharm:reharmonization` (`E0002.md` 작성), 몇 주 뒤**

새 독립 논문이 `.raw/`에 들어왔습니다(`reharm:root` 경유). Phase A가 E0001 노드를 재검증하니 여전히 유효합니다. Phase C가 새 논문을 분해해 `claims/stable-embedding-required-for-8bit.md`(seed)를 파생시키고, 본 주장에 없던 **두 번째 독립 출처**를 공급합니다. 다시 반박을 견뎌 `generation 3`이 되고, *검증 생존 + 독립 출처 2개* 조건을 채워 이제 `developing → hardened`로 승급합니다.

**④ 모호한 것 판정 — `reharm:critique`**

두 출처가 충돌합니다. 하나는 모든 규모에서 품질이 유지된다 하고, 다른 하나는 ~65B를 넘어서면 저하가 나타난다고 보고합니다 — 그래서 노드에 `> [!contradiction]` 콜아웃이 달려 있습니다. `reharm:critique`가 이 백로그를 모아 당신을 인터뷰하고, 당신은 *"주장을 ≤65B로 한정하고 >65B는 열린 질문으로 둔다"* 고 판정합니다. 콜아웃은 제거되어 `## Objections & Limits`로 흡수되고, 날카로워진 질문이 `questions/`에 적재되며 `confidence`가 재확인됩니다. 유의할 점: critique는 `confidence`·`status`만 조정할 뿐 **`generation`은 절대 올리지 않습니다**(세대는 당신의 판정이 아니라 반박 생존으로만 얻으니까요).

**⑤ 평행 스코프에서 빌려오기 — `reharm:modal-interchange`**

```bash
/reharm:modal-interchange Research_optimizers Research_serving
```

두 스코프를 가볍게 정찰하면(`hot.md` → `index.md`) 교차점이 드러납니다. 서빙 스코프의 *"INT8 가중치 양자화는 정확도를 유지하려면 채널별 캘리브레이션이 필요하다"* 와 옵티마이저 스코프의 *"8-bit는 안정적 임베딩 레이어가 필요하다"* 가 사실 **같은 실패 모드**입니다 — 민감한 한 레이어에서 양자화가 깨지고, 그 레이어를 구조적으로 붙들어야 풀린다는 것. 이 스코프에 `mashups/quantization-stability-shared-failure-mode.md`(seed로 탄생)를 발행하고, 그 `sources:`는 양쪽 원본 노드를 wikilink로 겁니다. 서빙 노드는 인용만 할 뿐 복사하거나 수정하지 않으며(단일 진실 공급원), 이 mashup도 이후 세션에서 다른 노드처럼 자연선택을 거칩니다.

**⑥ 실세계 증명 → `evergreen`**

돌리기 전에 `reharm:experiment-design`으로 실험을 **사전 등록**합니다 — 먼저 걸린 결정을 명명하게 하고(CONFIRM → 8-bit Adam을 학습 설정에 유지 / REFUTE → 32-bit로 되돌리고 메모리 예산 재편성), confirm/refute 기준(≤65B에서 eval-loss 격차가 허용치 미만이면 CONFIRM)을 미리 못 박아 결과를 사후에 합리화할 수 없게 하고, 목표를 외부 러너에 넘깁니다. 마침내 실제 파이프라인에서 8-bit Adam을 돌립니다. 당신의 규모(≤65B)에서 32-bit와 노이즈 범위 안에서 일치합니다. 실험 보고서는 스코프의 `.raw/experiments-results/`에 안착하고(현장 출처 관례), `reharm:root`로 `sources/` 요약이 생깁니다. 다음 `reharm:reharmonization`의 Phase C가 그 결론을 — **성립 조건(≤65B)과 함께** — 주장의 `## Field Evidence`로 import합니다. 그 조건이 주장의 적용 범위(④에서 ≤65B로 한정한 것)와 맞아떨어지고 미해결 반례도 없으므로, 이 단 하나의 현장 근거가 마지막 관문을 엽니다: `hardened → evergreen`. (실험이 더 좁은 조건에서만 일치했다면, 주장을 그 조건에 맞춰 더 좁히거나 evergreen을 보류했을 것입니다.)

**⑦ 결정에 답하기 — `reharm:ensemble`**

D1에 답할 수 있게 되었으니 페이지 하나를 얻습니다: `deliverables/8bit-adam-answer.md`, `question:`은 `D1`. 하중을 받는 모든 문장이 스냅샷과 함께 노드를 인용하고(`[[8bit-adam-matches-32bit-quality]] evergreen · high · g5`), 헤더의 **신뢰도 하한**은 가장 약한 하중 주장이 정하며, ④에서 열어 둔 >65B 질문은 `## Open caveats`에 그대로 남습니다. 나중에 세션을 더 거친 뒤 ensemble을 다시 돌리면 같은 파일이 제자리에서 재도출됩니다. 답변이 위키를 따라가지 그 반대가 아니며, 어떤 노드의 상태도 바뀌지 않습니다.

**⑧ 매듭짓고, 그걸 떠받쳤던 가지 치기 — `reharm:critique`**

답에 따라 실행하고 D1을 `settled`로 넘깁니다. 다음 세션의 가지치기 훑기가 D1만 떠받치던 노드들 — 벤치마크 경계, 메모리 절감 비율 세부 — 을 가지치기 후보로 올립니다. 아직 열린 다른 결정에도 걸리는 둘은 남기고 나머지는 자릅니다: `status: pruned`, 본문 그대로, 세대 그대로, 들어오는 위키링크도 계속 해소됩니다. 더 이상 의미가 없어진 그날부터 반박자와 재검증을 안 끌어가고, 혹시 D1이 다시 열리면 그대로 되돌아옵니다.

**세션 사이에 읽는 것:** `index.md`(맨 위 **결정 표** — 각 결정이 어디까지 왔는지 — 그다음 성숙도 통계), `hot.md`(방금 바뀐 것), `meta/evolution/E####.md`(왜 바뀌었는지, `## Decision movement` 한 줄과 함께). 또는 `reharm:pushing`을 돌리면 대신 읽고 다음 수를 짚어 줍니다(read-only).

</details>

## 설치

```bash
# GitHub에서
claude plugin marketplace add hwang-yeonsu/re-harmoniz
claude plugin install reharm@re-harmoniz

# 또는 로컬 클론에서
claude plugin marketplace add /path/to/re-harmoniz
claude plugin install reharm@re-harmoniz
```

**프로젝트 단위로 활성화(권장).** 설치는 플러그인을 *사용 가능한* 상태로만 만듭니다. **`/reharm:*`이 어디에 존재하는지는 활성화(enablement)가 결정**하고, 이는 프로젝트 루트 단위로 해석됩니다. 사용자(user) 레벨에서는 꺼 두고, 실제로 연구 위키를 담는 repo에서만 켜세요 — `<repo-root>/.claude/settings.json`:

```json
{ "enabledPlugins": { "reharm@re-harmoniz": true } }
```

이후 업데이트는 `claude plugin update reharm@re-harmoniz`.

요구 사항: Claude Code + Python 3 (표준 라이브러리만 씁니다 — frontier 스코어러와 위키 linter). 웹 검색은 네이티브 도구를 사용합니다. *선택:* `npm install -g defuddle`을 깔면 웹페이지를 더 깔끔하고 토큰도 덜 쓰며 추출할 수 있습니다. `reharm`은 이게 있으면 쓰고 없으면 네이티브 WebFetch로 폴백합니다(`EVOLUTION.md` §6).

## 스코프 내부

**스코프**는 자기완결적인 폴더입니다. 다음 세 가지가 폴더를 스코프로 만듭니다:

```
Research_X/
├── .raw/            # 불변 출처 (논문, 클립, 덤프)
│   ├── experiments-results/ # 현장 출처 — 스코프 자체 실험/실세계 결과
│   └── deep-research/       # 딥리서치 승격(§13)에서 돌아오는 보고서
├── wiki/
│   ├── claims/      # ★ 당신의 결정이 딛고 선 단언 — 진화의 단위
│   ├── mashups/     # ★ 합성된 교차 통찰
│   ├── sources/     # 출처 1개당 요약 페이지 1개 (origin: primary|secondary + 계보)
│   ├── questions/   # 열린 질문 — 생명주기: open → answered | escalated | archived
│   ├── experiments/ # ★ 현장 실험 사전 등록 (설계 기록)
│   ├── deliverables/ # 답변 합성 — 진화하지 않는 스냅샷 (reharm:ensemble)
│   ├── meta/evolution/  # 세션 보고서 E0001.md…
│   └── index.md · hot.md · log.md · overview.md
└── CLAUDE.md        # 스코프 설정 — Goal & Open Decisions 블록 포함 (templates/SCOPE_CLAUDE.md)
```

`sources/` = 문서가 말하는 것(기록으로 남은 증언). `claims/` = 당신의 결정이 딛고 선 가지. 진화하는 것은 claims와 mashups뿐이고, 그것도 어떤 결정이 아직 필요로 하는 동안만입니다.

`CLAUDE.md`의 결정 블록이 하중을 받는 부분입니다: 씨앗 투입을 선별적으로, 표적 선정을 결정 범위로, 검증을 계층으로 만들고, 가지치기를 가능하게 하는 게 이 블록입니다. 이게 없는 스코프도 예전과 똑같이 돌아갑니다 — 관련 규칙이 전부 잠들어 있을 뿐이고, linter가 그렇다고 알려 줍니다.

## 이미 쓰고 있는 구조에 맞춰

스코프는 *그저* `.raw/` + `wiki/` + `CLAUDE.md`일 뿐이라 어떤 지식 베이스에도 끼워 넣을 수 있습니다 — reharm은 스코프가 어디에 놓이든 상관하지 않습니다. 배치 예시 하나: 개인 PARA / Obsidian vault 안에 연구 스코프를 중첩하고, 프로젝트에 묶인 연구는 해당 프로젝트 아래에, 범용 참조 연구는 resources 아래에 두는 식입니다.

```
my-vault/                       # 당신의 지식 베이스 루트 (예: Obsidian vault)
├── 00_Inbox/
├── 01_Projects/                # 기한이 있는 업무
│   └── Project_A/
│       └── Research_X/          # ← reharm 스코프 (이 프로젝트에 종속된 연구)
│           ├── .raw/
│           ├── wiki/
│           └── CLAUDE.md
├── 02_Areas/
├── 03_Resources/               # 지속적 참조 자료
│   └── Research_Y/              # ← reharm 스코프 (범용 참조)
│       ├── .raw/
│       ├── wiki/
│       └── CLAUDE.md
└── 04_Archives/
```

이건 예시일 뿐이니 이미 쓰고 있는 구조를 그대로 쓰세요. (스코프는 코드 작업공간이 아니므로, 각 스코프의 `CLAUDE.md`에 실제 소스코드 경로를 적어 두세요.)

## 자율 모드 (opt-in)

위의 모든 스킬은 **설계상 수동**입니다 — 표적도 당신이 고르고, 판정도 당신이 합니다(`EVOLUTION.md`의 "자동 결정은 없다"). 루프를 *무인(unattended)*으로 돌리고 싶을 때를 위해, 플러그인은 그 원칙을 일부러 내려놓는 템플릿을 함께 제공합니다: [`templates/loop.md`](templates/loop.md). 단 하나는 내려놓지 않습니다: 루프는 결정을 쓰지도, 매듭짓지도 않습니다. 열린 결정이 없으면 스스로 표적을 고르는 대신 깨끗하게 멈춥니다(`no-decisions`) — 목표를 스스로 만들어 내는 루프는 눈에 띈 아무거나 최적화하게 되니까요. 연구 프로젝트의 `.claude/loop.md`로 복사하고 `CONFIG` 블록을 채우면, 네이티브 `/loop` 명령이 **한 번 돌 때마다 iteration을 하나씩** 재실행합니다 — `reharm:pushing`이 다음 수를 고르고, 추천된 스킬이 실행되며, 메인 세션이 당신의 승인을 대행합니다.

가장 빠른 길은 번들된 위자드입니다 — **명령 하나로 설정부터 실행까지**:

```bash
/reharm:loop-setup       # 스코프 탐지 → 열린 결정 확인 → CONFIG 인터뷰 → 실험 게이트 사전 검증 →
                         # .claude/loop.md 작성 → 같은 호출 안에서 네이티브 /loop 시작
```

손으로 복사할 필요는 없습니다 — 위자드가 `.claude/loop.md`를 대신 써 줍니다. 수동 설정(템플릿 복사 후 CONFIG 직접 채우기)도 여전히 유효한 대안입니다. 어느 쪽이든 이 파일은 연구 프로젝트 소유의 그 시점 사본이라 플러그인을 업그레이드해도 갱신되지 않으니, 업그레이드 후에는 위자드를 다시 돌려 새로 쓰세요(기존 CONFIG는 보여주고 유지하며, 원장은 그대로 이어지고, 스코프/위키에는 마이그레이션이 필요 없습니다). 루프 실행은:

```bash
# 연구 프로젝트 루트에서 — 프롬프트 없는 /loop(맨손 또는 인터벌만)이 .claude/loop.md를 읽습니다
/loop                    # 권장 — dynamic, self-paced: MAX_ITERS를 강제하고, 할 일이 없거나 정체되면 스스로 멈춥니다
/loop 2h                 # 지원 — 고정 간격; 자기 cron 작업을 지워서 종료합니다 (인터벌만, 프롬프트 금지)
```

이 모드는 자동 결정 금지 원칙을 깨기 때문에 **opt-in이고 플러그인 코어 바깥**에 둡니다(스킬이 아니라 프로젝트 로컬 파일). 안전장치는 계약에 못 박혀 있습니다: 스코프당 lock, 스코프 *바깥*에 두는 ledger(`EVOLUTION.md` §8), iteration당 표적 상한(`MAX_TARGETS`, 기본 2), 되돌릴 수 있는 `deprecate`(절대 삭제하지 않음), 감사를 위한 이중 로깅(`E####.md` + 건드린 `targets`를 적는 ledger 한 줄). 실제 실험 실행은 게이트로 막혀 있습니다 — `RUN_EXPERIMENTS=yes`이면서 **동시에** 스코프의 코드 워크스페이스 경로가 있어야만 돌아가고(§12), 실행 자체는 격리된 백그라운드 러너 서브에이전트(기본은 플러그인의 runner-worker, 외부 러너를 설정했다면 그것)가 맡아 `.raw/experiments-results/`로 보고합니다. 조건이 안 되면 설계 + handoff에서 멈춥니다.

**어디서 도는가:** `/loop`은 **로컬이고 세션에 묶여 있습니다** — 돌아가려면 Claude Code 세션이 열려 있고 머신이 깨어 있어야 합니다(닫히거나 잠든 노트북에서는 돌지 않습니다). 템플릿은 두 모드 어느 쪽으로도 돕니다: 맨손 `/loop`(**dynamic**, self-paced — 권장; 종료가 fail-safe라서, 다음 깨어남을 재예약하지 않는 것만으로 멈춥니다) 또는 인터벌만 준 `/loop 2h`(**고정 간격** — 루프가 자기 cron 작업을 직접 지워야 끝나고, 지우기를 놓치면 no-op tick이 CronDelete로 잡을 지우거나 7일 만료까지 반복됩니다). 인터벌과 함께 프롬프트를 주지 마세요 — 프롬프트가 있으면 `.claude/loop.md`를 건너뜁니다. 도중 compact는 안전하고(상태는 ledger에 있고, 다음 발화가 파일 전문을 다시 읽습니다) `/clear`는 스케줄을 죽입니다. 고정된 벽시계 일정(예: 야간)이나 노트북을 닫은 채 무인으로 돌리려면, Anthropic 관리 인프라에서 실행되는 클라우드 [Routines](https://code.claude.com/docs/en/routines.md)(`/schedule`)를 쓰세요 — `/loop`이 아닙니다. 템플릿 헤더는 간결한 계약서이고, 긴 설명(무엇·왜·어떻게 검증하는지·실행 모델·정확한 명령)은 **[자율 루프 가이드](templates/loop.guide.ko.md)**에 있습니다.

## 언어

당신의 노트, 주장, 보고서는 **당신의 언어**로 작성됩니다(한국어 완전 지원 — 이를 가능케 하는 검색 규칙은 `EVOLUTION.md` §9 참고). 시스템 문서(이 README, `EVOLUTION.md`, 스킬)는 영어로 되어 있습니다.
