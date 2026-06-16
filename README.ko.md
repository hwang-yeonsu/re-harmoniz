# re:Harmoniz

[English](README.md) · **한국어**

> **연구 위키를 위한 진화 루프(evolution loop)** — Claude Code 플러그인 (`reharm`).

**re:Harmoniz = re·search(연구) + re·harmoniz·ation(재화성).** 음악가가 멜로디를 재화성하듯 — 선율은 그대로 두고 그 아래 화성(코드)을 다시 짜듯 — re:Harmoniz는 연구 *질문*은 고정한 채 **그 아래를 떠받치는 주장(claim)과 근거**를 세대를 거듭하며 다시 도출합니다.

지식은 원자적 **claim**(주장) 노드로 존재하며, 두 가지 압력 아래에서 단단해집니다: **변이(mutation, 수정)** 와 **자연선택(natural selection, 적대적 검증)**. 1세대 주장은 헐벗은 단언이지만, 10세대 주장은 자신을 향한 반박을 흡수했고 독립적인 출처를 인용하며 실제 현장 근거를 갖춥니다. *살아남은* 노드만 세대를 얻기에, 위키의 평균 신뢰도는 단조 증가합니다.

전부 당신이 소유하는 순수 Markdown입니다. 프로토콜 전체는 단 하나의 파일에 담겨 있습니다: [`EVOLUTION.md`](EVOLUTION.md).

## 그냥 위키와 뭐가 다른가

대부분의 지식 도구 — Zettelkasten vault, Notion, "LLM 위키" 노트 저장소 — 는 **축적**합니다: 더하는 모든 노트가 동등하게 취급되고, 더미는 커지기만 합니다. re:Harmoniz는 **연구**를 위해 만들어졌습니다 — 연구에서 대부분의 단언은 입증되기 전까지 틀린 것이라서, 정반대로 동작합니다. 아는 것에 **등급을 매기고 단단하게** 만듭니다:

- **신뢰도는 가정이 아니라 획득입니다.** 모든 주장은 적대적 반박자 3인에게 압력 시험을 받고, 살아남은 것만 세대를 얻습니다. 평균 신뢰도가 더미와 함께 표류하지 않고 단조 증가합니다.
- **성숙도는 나이가 아니라 근거로 열립니다.** `seed → developing → hardened → evergreen`은 노트가 얼마나 오래 방치됐는지가 아니라 독립 출처와 실세계 현장 근거로 승급합니다.
- **이견은 기록에 남습니다.** 모순은 당신이 판정하기 전까지 *양쪽* 노드에 살아 있고, 붕괴한 주장은 삭제가 아니라 deprecated 됩니다. 위키가 자기 결론을 스스로 방어합니다.

그게 차이입니다: 노트 저장소가 아니라 **아는 것을 단단하게 만드는, 연구 특화 주장-진화 엔진**.

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

새 자료나 새 의심이 쌓일 때마다 돌리세요. 자동 결정은 없습니다: 표적도 당신이 고르고, 모호한 것도 당신이 판정합니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `reharm:root` | 진입점. 스코프를 스캐폴딩한 뒤 씨앗을 투입합니다: repo URL, 글, 의사코드, 기존 노트, 막연한 아이디어를 던지면 → `.raw/`에 안착하고 원자적 `claims/`(전부 1세대로 탄생)가 됩니다. |
| `reharm:reharmonization` | 한 번의 진화 세션 — 프로젝트명의 유래가 된 스킬: 회고 → 표적(당신이 승인) → 변이 → 자연선택(반박자 3인, 2/3 이상 생존 필요) → 기록. |
| `reharm:modal-interchange` | 스코프 간 매시업 — 평행 스코프에서 지식을 빌려와(평행 선법에서 코드를 빌려오듯) 도메인 교차 통찰을 발행, 인용 전용. |
| `reharm:critique` | 판정 — 모호한 백로그(열린 질문, 정체된 노드, 모순, lint 경고)를 모아 짧은 인터뷰로 해소합니다. |
| `reharm:pushing` | 방향 잡기(read-only). 스코프의 현재 위키·진화 상태를 읽어 다음 수 — 씨앗 투입, 진화, 판정 — 를 근거와 함께 추천합니다. 아무것도 바꾸지 않으며, 결정은 당신이 합니다. |

## 사용 시나리오

**빠르게 바뀌는 기법 추적.** 새로운 ML 최적화 기법이 대규모에서도 정말 통하는지 평가 중입니다. 논문 몇 편과 레퍼런스 repo를 `reharm:root`하면 각 발견이 주장이 됩니다. 몇 주 뒤 새 결과가 그중 하나를 반박하면 — `reharm:reharmonization`을 실행: 반박자들이 양쪽을 시험하고, 패배한 쪽은 *이유와 함께 기록으로 남긴 채* deprecated 되며, 살아남은 쪽은 세대를 얻고 이제 독립적인 출처 2개를 인용합니다.

**스스로 방어하는 문헌 리뷰.** 모든 논문을 인용이 달린 주장으로 원자화합니다. 논문 간 모순은 당신이 `reharm:critique`에서 정리하기 전까지 *양쪽* 노드에 명시된 채 유지됩니다. `index.md` 성숙도 통계가 무엇이 단단하고(hardened/evergreen) 무엇이 아직 추측인지(seed)를 한눈에 보여줍니다.

**경쟁 / 시장 분석.** 벤더 문서, 벤치마크, 현장 보고를 씨앗으로 투입합니다. 적대적 검증이 독립적 뒷받침 없는 마케팅 주장을 걸러내고, 근거 렌즈를 통과한 단언만 단단해집니다. 나중에 주장을 확인하거나 깨뜨리는 실사용 결과는 `## Field Evidence` 아래에 덧붙습니다.

**두 연구 트랙 연결.** 스코프가 둘 생기면 — 가령 하나는 *학습*, 하나는 *서빙* — `reharm:modal-interchange`가 한쪽의 미해결 문제를 다른 쪽의 메커니즘이 답하는 지점을 찾아, 양쪽 원본에 인용을 건(단일 진실 공급원) 도메인 교차 통찰을 발행합니다.

**식은 스코프로 돌아왔을 때.** 몇 주 뒤 스코프를 다시 열었는데 어디까지 했는지 기억나지 않습니다. `reharm:pushing`이 성숙도 통계, frontier 점수, 열린 모순, 직전 세션의 stagnation 판정을 읽고 다음 수를 짚어줍니다 — *새 자료 씨앗 투입*(`root`), *frontier 노드 진화*(`reharmonization`), 또는 *백로그 판정*(`critique`) — 각각의 근거와 함께. read-only입니다: 가리킬 뿐, 결정과 실행은 당신이 합니다.

<details>
<summary><b>전체 워크스루 — 한 주제로 4개 스킬 전부 거치기</b></summary>

스코프는 `Research_optimizers`(학습 단계 최적화)이고, 추론용 평행 스코프 `Research_serving`이 이미 존재합니다. **질문:** *8-bit Adam(bitsandbytes)이 최종 모델 품질을 해치지 않고 32-bit Adam을 대체할 수 있는가?*

**① 씨앗 투입 — `reharm:root`**

```bash
cd 01_Projects/Project_A/Research_optimizers
/reharm:root https://github.com/bitsandbytes-foundation/bitsandbytes
/reharm:root "논문: 8-bit Optimizers via Block-wise Quantization (Dettmers et al., 2022)"
```

repo 덤프와 논문이 `.raw/`에 안착하고 각각 `sources/` 요약이 생기며, 단언은 주장이 됩니다 — `claims/8bit-adam-matches-32bit-quality.md`, `seed · generation 1 · confidence low`로 탄생.

**② 첫 진화 — `reharm:reharmonization` (`E0001.md` 작성)**

Phase B가 새 노드를 표면화(높은 boundary score)하고 당신이 승인합니다. Phase C는 반대 근거를 웹에서 사냥합니다. Phase D는 반박자 3인 — *일관성 · 근거 · 재현성* — 을 돌리고, 재현성 렌즈가 반례(*안정적 임베딩 레이어 없이는 학습이 발산*)를 들이밀지만 **3 중 2 생존**.

→ `generation → 2`, `seed → developing`, `confidence medium`; 반례는 주장의 `## Objections & Limits`로 흡수; `E0001.md`가 세 판정을 기록; `index.md` + `hot.md` 갱신. *아직 `hardened`는 아닙니다 — 그 관문은 **독립** 출처가 하나 더 필요합니다.*

**③ 둘째 진화 — `reharm:reharmonization` (`E0002.md` 작성), 몇 주 뒤**

새 독립 논문이 `.raw/`에 들어왔습니다(`reharm:root` 경유). Phase A가 E0001 노드를 재검증 — 여전히 유효. Phase C가 새 논문을 분해해 `claims/stable-embedding-required-for-8bit.md`(seed)를 파생시키고, 본 주장에 없던 **두 번째 독립 출처**를 공급합니다. 다시 반박을 견뎌 → `generation 3`, 그리고 *검증 생존 + 독립 출처 2개* 조건을 충족해 이제 `developing → hardened`로 승급합니다.

**④ 모호한 것 판정 — `reharm:critique`**

두 출처가 충돌합니다: 하나는 모든 규모에서 품질이 유지된다 하고, 다른 하나는 ~65B 초과에서 저하를 보고 — 그래서 노드에 `> [!contradiction]` 콜아웃이 달려 있습니다. `reharm:critique`가 이 백로그를 모아 당신을 인터뷰하고, 당신은 *"주장을 ≤65B로 한정하고, >65B는 열린 질문으로 둔다"* 고 판정합니다. 콜아웃은 제거돼 `## Objections & Limits`로 흡수되고, 날카로워진 질문이 `questions/`에 적재되며 `confidence`가 재확인됩니다. 유의: critique는 `confidence`/`status`만 조정하고 **`generation`은 절대 올리지 않습니다**(세대는 당신의 판정이 아니라 반박 생존으로만 얻습니다).

**⑤ 평행 스코프에서 빌려오기 — `reharm:modal-interchange`**

```bash
/reharm:modal-interchange Research_optimizers Research_serving
```

두 스코프의 값싼 정찰(`hot.md` → `index.md`)이 교차점을 찾아냅니다: 서빙 스코프의 *"INT8 가중치 양자화는 정확도 유지를 위해 채널별 캘리브레이션이 필요"* 와 옵티마이저 스코프의 *"8-bit는 안정적 임베딩 레이어가 필요"* 가 **같은 실패 모드** — 민감한 한 레이어에서 양자화가 깨지며, 구조적으로 고정해야 풀린다는 것. 이 스코프에 `mashups/quantization-stability-shared-failure-mode.md`(seed로 탄생)를 발행하고, 그 `sources:`는 양쪽 원본 노드를 wikilink로 겁니다. 서빙 노드는 인용만 할 뿐 복사·수정하지 않으며(단일 진실 공급원), 이 mashup도 이후 세션에서 다른 노드처럼 자연선택을 거칩니다.

**⑥ 실세계 증명 → `evergreen`**

마침내 실제 파이프라인에서 8-bit Adam을 돌립니다; 당신의 규모(≤65B)에서 32-bit와 노이즈 범위 내로 일치합니다. 실험 보고서가 `reharm:root`로 들어오고, 그 결론이 주장의 `## Field Evidence` 아래에 wikilink와 함께 덧붙습니다. 다음 세션에서 그 단 하나의 현장 근거 항목이 마지막 관문을 엽니다: `hardened → evergreen`.

**세션 사이에 읽는 것:** `hot.md`(방금 바뀐 것), `index.md`(성숙도 통계 — 각 상태에 노드가 몇 개인지), `meta/evolution/E####.md`(왜 바뀌었는지) — 또는 `reharm:pushing`을 돌리면 이 셋을 대신 읽고 다음 수를 짚어줍니다(read-only).

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

**프로젝트 단위로 활성화(권장).** 설치는 플러그인을 *사용 가능* 상태로만 만듭니다; **`/reharm:*`이 어디에 존재하는지는 활성화(enablement)가 결정**하며, 프로젝트 루트 단위로 해석됩니다. 사용자(user) 레벨에서는 꺼 두고, 실제로 연구 위키를 담는 repo에서만 켜세요 — `<repo-root>/.claude/settings.json`:

```json
{ "enabledPlugins": { "reharm@re-harmoniz": true } }
```

이후 업데이트는 `claude plugin update reharm@re-harmoniz`.

요구 사항: Claude Code + Python 3 (표준 라이브러리만 — frontier 스코어러와 위키 linter). 웹 검색은 네이티브 도구를 사용합니다. *선택:* `npm install -g defuddle`을 설치하면 더 깔끔하고 토큰 효율적인 웹페이지 추출이 가능하며, `reharm`은 있으면 사용하고 없으면 네이티브 WebFetch로 폴백합니다(`EVOLUTION.md` §6).

## 스코프 내부

**스코프**는 자기완결적 폴더입니다 — 세 가지가 그것을 스코프로 만듭니다:

```
Research_X/
├── .raw/            # 불변 출처 (논문, 클립, 덤프, 실험 보고서)
├── wiki/
│   ├── claims/      # ★ 원자적 단언 — 진화의 단위
│   ├── mashups/     # ★ 합성된 교차 통찰
│   ├── sources/     # 출처 1개당 요약 페이지 1개
│   ├── questions/   # 열린 질문
│   ├── meta/evolution/  # 세션 보고서 E0001.md…
│   └── index.md · hot.md · log.md · overview.md
└── CLAUDE.md        # 스코프 설정 (templates/SCOPE_CLAUDE.md)
```

`sources/` = 문서가 말하는 것(기록된 증언). `claims/` = 당신이 현재 사실이라 믿는 것(다투어지는 쟁점). 진화하는 것은 claims와 mashups뿐입니다.

## 이미 쓰고 있는 구조에 맞춰

스코프는 *그저* `.raw/` + `wiki/` + `CLAUDE.md`일 뿐이라 어떤 지식 베이스에도 끼워 넣을 수 있습니다 — reharm은 스코프가 어디에 있는지 신경 쓰지 않습니다. 한 가지 배치 예시: 개인 PARA / Obsidian vault 안에 연구 스코프를 중첩하고, 프로젝트에 종속된 연구는 해당 프로젝트 아래에, 범용 참조 연구는 resources 아래에 둡니다.

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

이건 한 가지 예시일 뿐 — 이미 쓰고 있는 구조를 그대로 쓰세요. (스코프는 코드 작업공간이 아니므로, 각 스코프의 `CLAUDE.md`에 실제 소스코드 경로를 적어 두세요.)

## 언어

당신의 노트, 주장, 보고서는 **당신의 언어**로 작성됩니다(한국어 완전 지원 — 이를 가능케 하는 검색 규칙은 `EVOLUTION.md` §9 참고). 시스템 문서(이 README, `EVOLUTION.md`, 스킬)는 영어입니다.
