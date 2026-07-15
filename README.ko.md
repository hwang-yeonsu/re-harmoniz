# re:Harmoniz

[English](README.md) · **한국어**

> **연구 위키를 위한 진화 루프(evolution loop)** — Claude Code 플러그인 (`reharm`).

**re:Harmoniz = re·search(연구) + re·harmoniz·ation(재화성).** 연구 *질문*은 고정해 둔 채, 그 아래를 떠받치는 것 — **주장(claim)과 그 주장이 딛고 선 근거** — 을 세대를 거듭하며 다시 도출합니다. (이름은 음악 용어 *재화성(reharmonization)*에서 왔습니다: 멜로디는 그대로 두고 그 아래 화성만 다시 짠다는 뜻입니다.)

지식은 원자적 **claim**(주장) 노드로 존재하며, 두 가지 압력을 받아 단단해집니다: **변이(mutation, 수정)** 와 **자연선택(natural selection, 적대적 검증)**. 1세대 주장은 아직 뒷받침 없는 단언일 뿐이지만, 10세대 주장은 자신을 향한 반박을 흡수했고 독립 출처를 인용하며 실제 현장 근거까지 갖춥니다. *살아남은* 노드만 세대를 얻으므로, 위키의 평균 신뢰도는 단조적으로 올라가기만 합니다.

전부 당신 소유의 순수 Markdown입니다. 프로토콜 전체가 파일 하나에 담겨 있습니다: [`EVOLUTION.md`](EVOLUTION.md).

## 그냥 위키와 뭐가 다른가

대부분의 지식 도구 — Zettelkasten vault, Notion, 이른바 'LLM 위키' 노트 저장소 — 는 **축적**합니다. 새로 더한 노트가 다 똑같이 취급되고, 더미는 커지기만 하죠. re:Harmoniz는 **연구**를 위해 만들어졌습니다. 연구에서는 대부분의 단언이 입증되기 전까지 틀린 것이라, 이 도구는 정반대로 움직입니다. 아는 것에 **등급을 매기고 단단하게** 다집니다:

- **신뢰도는 거저 주어지지 않고 획득됩니다.** 모든 주장은 적대적 반박자 3인의 시험대에 오르고, 살아남은 것만 세대를 얻습니다. 노트가 쌓일수록 평균이 흐려지는 게 아니라, 평균 신뢰도가 오히려 단조적으로 올라갑니다.
- **성숙도는 나이가 아니라 근거로 열립니다.** `seed → developing → hardened → evergreen` 승급은 노트를 얼마나 오래 묵혔는지가 아니라 독립 출처와 실세계 현장 근거로 결정됩니다.
- **이견은 기록에 남습니다.** 모순은 당신이 판정하기 전까지 *양쪽* 노드에 살아 있고, 무너진 주장은 삭제되는 대신 deprecated 처리됩니다. 위키가 제 결론을 스스로 방어하는 셈입니다.

바로 그 점이 다릅니다. 이건 노트 저장소가 아니라 **아는 것을 단단하게 벼려 내는, 연구 특화 주장-진화 엔진**입니다.

## 루프

```
  주장 씨앗(seed)
      │
      ▼
  변이(mutate)        ── 수정, 새 출처 분해, 반대 근거 사냥
      │
      ▼
  자연선택            ── 반박자 3인, 각자 하나의 렌즈 (일관성 · 근거 · 재현성)
      │
      ├─ 2/3 이상 생존 ─▶ 세대 +1, 승급: seed → developing → hardened → evergreen
      └─ 붕괴          ─▶ deprecated (기록은 보존 — 절대 삭제하지 않음)
```

새 자료나 새 의심이 쌓일 때마다 돌리세요. 자동으로 결정되는 건 없습니다. 표적도 당신이 고르고, 모호한 것도 당신이 판정합니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `reharm:root` | 진입점. 스코프를 세팅한 뒤 씨앗을 투입합니다. repo URL, 글, 의사코드, 기존 노트, 막연한 아이디어를 던지면 `.raw/`에 안착하고 원자적 `claims/`(전부 1세대로 탄생)가 됩니다. 여러 출처는 격리된 sub-agent로 fan-out(출처당 하나)되므로, 한 출처의 서술 틀이 다른 출처의 주장으로 새어들지 않습니다. |
| `reharm:reharmonization` | 한 번의 진화 세션 — 프로젝트 이름의 유래가 된 스킬입니다: 회고 → 표적(당신이 승인) → 변이 → 자연선택(반박자 3인, 2/3 이상 생존해야 함) → 기록. |
| `reharm:modal-interchange` | 스코프 간 매시업 — 평행 스코프에서 지식을 빌려와(평행 선법에서 코드를 빌려오듯) 도메인 교차 통찰을 발행합니다. 인용 전용. 각 매쉬업은 원본 상태의 `borrowed:` 스냅샷을 지니므로, 나중에 원본이 바뀌면 조용한 부패 대신 objection으로 드러납니다. |
| `reharm:critique` | 판정 — 모호한 백로그(열린 질문, 정체된 노드, 모순, lint 경고)를 모아 짧은 인터뷰로 풀어냅니다. 테마가 비슷한 것들은 멀티셀렉트 일괄 triage(승격 / 보류 / 보관) 한 번으로, 4세션 넘게 방치된 열린 질문은 자동 보관 없이 노화 묶음으로 제안합니다. |
| `reharm:pushing` | 방향 잡기(read-only). 스코프의 현재 위키·진화 상태를 읽어 다음 수 — 씨앗 투입, 진화, 판정, 또는 막힌 근거의 딥리서치 승격 — 를 근거와 함께 추천합니다. 아무것도 바꾸지 않고, 결정은 당신 몫입니다. |
| `reharm:experiment-design` | 현장 실험 설계자. `hardened → evergreen` 관문에 막힌 주장을 두고, 그것을 확증하거나 반증할 실험을 **사전 등록**합니다 — 가설, 실행 전에 못 박은 CONFIRM/REFUTE 기준, 기록할 조건. 그런 다음 쉬운 말로 정리한 목표를 러너에 넘깁니다 — 직접 설정한 외부 러너(예: `autoresearch`)일 수도 있고, 기본값은 플러그인의 **runner-worker**(노드에 기록해 두었다가 나중에 사용자나 자율 루프가 띄우는 격리 서브에이전트)입니다. 설계·기록만 할 뿐 코드는 절대 실행하지 않습니다. |
| `reharm:ensemble` | 답변 합성 — 루프의 **출구**. 살아남은 것들을 모아 스코프의 중심 질문에 답하는 `deliverables/` 페이지 하나를 만듭니다. 하중을 받는 모든 문장이 (status · confidence · generation) 스냅샷과 함께 노드를 인용하고, 가장 약한 하중 주장이 신뢰도 하한을 정하며, 남은 유의점은 기록에 남습니다. 같은 파일을 제자리에서 갱신할 뿐, 노드 상태는 절대 바꾸지 않습니다. |

> **뭘 돌려야 할지 모르겠다면?** [`docs/SKILLS.ko.md`](docs/SKILLS.ko.md)가 상황별로 친절하게 안내합니다 — *"이걸 하고 싶다 → 이걸 돌려라"* — 각 스킬이 무엇을 하고 무엇은 건드리지 않는지까지. (아니면 그냥 `reharm:pushing`을 돌리면 다음 수를 짚어 줍니다.)

## 사용 시나리오

**빠르게 바뀌는 기법 추적.** 새로운 ML 최적화 기법이 대규모에서도 정말 통하는지 평가하는 중입니다. 논문 몇 편과 레퍼런스 repo를 `reharm:root`하면 각 발견이 주장이 됩니다. 몇 주 뒤 새 결과가 그중 하나를 반박하면 `reharm:reharmonization`을 돌리세요. 반박자들이 양쪽을 시험하고, 진 쪽은 *이유와 함께 기록에 남은 채* deprecated 되며, 살아남은 쪽은 세대를 얻고 이제 독립 출처 2개를 인용합니다.

**스스로 방어하는 문헌 리뷰.** 논문마다 인용을 단 주장으로 원자화합니다. 논문 사이의 모순은 당신이 `reharm:critique`에서 정리하기 전까지 *양쪽* 노드에 명시된 채 남습니다. `index.md`의 성숙도 통계가 무엇이 단단하고(hardened/evergreen) 무엇이 아직 추측인지(seed)를 한눈에 보여 줍니다.

**경쟁 / 시장 분석.** 벤더 문서, 벤치마크, 현장 보고를 씨앗으로 넣습니다. 적대적 검증이 독립적 뒷받침 없는 마케팅 주장을 걸러 내고, 근거 렌즈를 통과한 단언만 단단해집니다. 나중에 그 주장을 확인하거나 뒤엎는 실사용 결과는 `## Field Evidence` 아래에 덧붙습니다.

**두 연구 트랙 연결.** 스코프가 둘 생기면 — 가령 하나는 *학습*, 하나는 *서빙* — `reharm:modal-interchange`가 한쪽의 미해결 문제를 다른 쪽 메커니즘이 답하는 지점을 찾아냅니다. 그리고 양쪽 원본을 함께 인용하는(단일 진실 공급원) 도메인 교차 통찰을 발행합니다.

**한동안 놔뒀던 스코프로 돌아왔을 때.** 몇 주 만에 스코프를 다시 열었는데 어디까지 했는지 기억나지 않습니다. `reharm:pushing`이 성숙도 통계, frontier 점수, 열린 모순, 직전 세션의 stagnation 판정을 읽고 다음 수를 짚어 줍니다 — *새 자료 씨앗 투입*(`root`), *frontier 노드 진화*(`reharmonization`), 또는 *백로그 판정*(`critique`) — 각각의 근거와 함께. read-only라서 가리키기만 할 뿐, 결정과 실행은 당신이 합니다.

<details>
<summary><b>전체 워크스루 — 한 주제로 7개 스킬 전부 거치기</b></summary>

스코프는 `Research_optimizers`(학습 단계 최적화)이고, 추론용 평행 스코프 `Research_serving`이 이미 존재합니다. **질문:** *8-bit Adam(bitsandbytes)이 최종 모델 품질을 해치지 않고 32-bit Adam을 대체할 수 있는가?*

**① 씨앗 투입 — `reharm:root`**

```bash
cd 01_Projects/Project_A/Research_optimizers
/reharm:root https://github.com/bitsandbytes-foundation/bitsandbytes
/reharm:root "논문: 8-bit Optimizers via Block-wise Quantization (Dettmers et al., 2022)"
```

repo 덤프와 논문이 `.raw/`에 안착하고 각각 `sources/` 요약이 생기며, 단언은 주장이 됩니다 — `claims/8bit-adam-matches-32bit-quality.md`가 `seed · generation 1 · confidence low`로 태어납니다. `reharm:root`는 각 출처를 **격리된 sub-agent** 안에서 원자화하고, 메인 세션은 raw 본문이 아니라 정제된 초안 주장만 넘겨받습니다. 그래서 여러 출처를 한꺼번에 넣어도 한쪽의 서술 틀이 다른 쪽으로 새어들지 않습니다.

**② 첫 진화 — `reharm:reharmonization` (`E0001.md` 작성)**

Phase B가 새 노드를 끌어올리고(높은 boundary score) 당신이 승인합니다. Phase C는 웹에서 반대 근거를 찾아 나섭니다. Phase D는 반박자 3인 — *일관성 · 근거 · 재현성* — 을 돌리고, 재현성 렌즈가 반례(*안정적 임베딩 레이어 없이는 학습이 발산한다*)를 들이밀지만 **3 중 2가 생존**합니다.

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

돌리기 전에 `reharm:experiment-design`으로 실험을 **사전 등록**합니다 — confirm/refute 기준(≤65B에서 eval-loss 격차가 허용치 미만이면 CONFIRM)을 미리 못 박아 결과를 사후에 합리화할 수 없게 하고, 목표를 외부 러너에 넘깁니다. 마침내 실제 파이프라인에서 8-bit Adam을 돌립니다. 당신의 규모(≤65B)에서 32-bit와 노이즈 범위 안에서 일치합니다. 실험 보고서는 스코프의 `.raw/experiments-results/`에 안착하고(현장 출처 관례), `reharm:root`로 `sources/` 요약이 생깁니다. 다음 `reharm:reharmonization`의 Phase C가 그 결론을 — **성립 조건(≤65B)과 함께** — 주장의 `## Field Evidence`로 import합니다. 그 조건이 주장의 적용 범위(④에서 ≤65B로 한정한 것)와 맞아떨어지고 미해결 반례도 없으므로, 이 단 하나의 현장 근거가 마지막 관문을 엽니다: `hardened → evergreen`. (실험이 더 좁은 조건에서만 일치했다면, 주장을 그 조건에 맞춰 더 좁히거나 evergreen을 보류했을 것입니다.)

**⑦ 답변 합성 — `reharm:ensemble`**

단단한 코어가 갖춰졌으니, 원래의 질문 — *8-bit Adam이 품질 손실 없이 32-bit를 대체할 수 있는가?* — 이 마침내 답 한 페이지를 얻습니다: `deliverables/8bit-adam-answer.md`. 하중을 받는 모든 문장이 스냅샷과 함께 노드를 인용하고(`[[8bit-adam-matches-32bit-quality]] evergreen · high · g5`), 헤더의 **신뢰도 하한**은 가장 약한 하중 주장이 정하며, ④에서 열어 둔 >65B 질문은 `## Open caveats`에 그대로 남습니다. 나중에 세션을 더 거친 뒤 ensemble을 다시 돌리면 같은 파일이 제자리에서 재도출됩니다. 답변이 위키를 따라가지 그 반대가 아니며, 어떤 노드의 상태도 바뀌지 않습니다.

**세션 사이에 읽는 것:** `hot.md`(방금 바뀐 것), `index.md`(성숙도 통계 — 각 상태에 노드가 몇 개인지), `meta/evolution/E####.md`(왜 바뀌었는지). 또는 `reharm:pushing`을 돌리면 이 셋을 대신 읽고 다음 수를 짚어 줍니다(read-only).

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
│   ├── claims/      # ★ 원자적 단언 — 진화의 단위
│   ├── mashups/     # ★ 합성된 교차 통찰
│   ├── sources/     # 출처 1개당 요약 페이지 1개 (origin: primary|secondary + 계보)
│   ├── questions/   # 열린 질문 — 생명주기: open → answered | escalated | archived
│   ├── experiments/ # ★ 현장 실험 사전 등록 (설계 기록)
│   ├── deliverables/ # 답변 합성 — 진화하지 않는 스냅샷 (reharm:ensemble)
│   ├── meta/evolution/  # 세션 보고서 E0001.md…
│   └── index.md · hot.md · log.md · overview.md
└── CLAUDE.md        # 스코프 설정 (templates/SCOPE_CLAUDE.md)
```

`sources/` = 문서가 말하는 것(기록으로 남은 증언). `claims/` = 당신이 지금 사실이라 믿는 것(다투어지는 쟁점). 진화하는 것은 claims와 mashups뿐입니다.

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

위의 모든 스킬은 **설계상 수동**입니다 — 표적도 당신이 고르고, 판정도 당신이 합니다(`EVOLUTION.md`의 "자동 결정은 없다"). 루프를 *무인(unattended)*으로 돌리고 싶을 때를 위해, 플러그인은 그 원칙을 일부러 내려놓는 템플릿을 함께 제공합니다: [`templates/loop.md`](templates/loop.md). 연구 프로젝트의 `.claude/loop.md`로 복사하고 `CONFIG` 블록을 채우면, 네이티브 `/loop` 명령이 **한 번 돌 때마다 iteration을 하나씩** 재실행합니다 — `reharm:pushing`이 다음 수를 고르고, 추천된 스킬이 실행되며, 메인 세션이 당신의 승인을 대행합니다.

가장 빠른 길은 번들된 위자드입니다 — **명령 하나로 설정부터 실행까지**:

```bash
/reharm:loop-setup       # 스코프 탐지 → CONFIG 인터뷰 → 실험 게이트 사전 검증 → .claude/loop.md 작성 →
                         # 같은 호출 안에서 네이티브 /loop 시작
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
