# TinyTapeout Submission & CI Troubleshooting Record

본 문서는 TinyTapeout 셔틀 제출 과정에서 발생한 **Top Module 이름 충돌(Naming Collision)**과 **CI 워크플로우 실패(`No tt_submission artifact found`)** 문제의 원인 및 해결 과정을 기록한 문서입니다.

---

## 1. Top Module 이름 충돌 해결 (Naming Collision)

### 1.1 문제 현상
TinyTapeout 제출 시 다음 에러가 발생:
> `There is another project using "tt_um_bgr_ldo_shuttle" as a top module name. Please rename your top module.`

### 1.2 원인
TinyTapeout은 전체 셔틀에 제출되는 모든 프로젝트의 Top Module 이름이 전역적으로 고유(Unique)해야 합니다. 일반적인 이름(`tt_um_bgr_ldo_shuttle`)은 다른 제출자가 이미 선점하여 충돌이 발생했습니다.

### 1.3 해결 내용
TinyTapeout 권장 규칙(`tt_um_<github_username>_<project>`)에 따라 탑 모듈명을 **`tt_um_wecallemjazzyfact_bgr_ldo`** 로 변경하고 관련 파일들을 일괄 갱신 및 재빌드했습니다.

- **모듈 설정 및 래퍼 수정**:
  - `info.yaml`: `top_module: "tt_um_wecallemjazzyfact_bgr_ldo"`
  - `src/project.v`: `module tt_um_wecallemjazzyfact_bgr_ldo (...)`
  - `src/tt_um_wecallemjazzyfact_bgr_ldo.v`: 신규 래퍼 파일 생성 (구 `src/tt_um_bgr_ldo_shuttle.v` 정리)
- **빌드 자동화 스크립트 수정**:
  - `build_gds.py`: Top Cell 명칭 및 출력 경로(`gds/tt_um_wecallemjazzyfact_bgr_ldo.gds`) 업데이트
  - `build_lef.py`: Macro 명칭 및 출력 경로(`lef/tt_um_wecallemjazzyfact_bgr_ldo.lef`) 업데이트
- **산출물 재생성**:
  - `gds/tt_um_wecallemjazzyfact_bgr_ldo.gds` (GDS Top cell 리네임 후 재빌드)
  - `lef/tt_um_wecallemjazzyfact_bgr_ldo.lef` 및 `gds/tt_um_wecallemjazzyfact_bgr_ldo.lef` (MACRO 명칭 갱신)
  - `gds/tt_um_wecallemjazzyfact_bgr_ldo.v` 생성 및 이전 이름 파일 정리

---

## 2. CI 실패 및 `No tt_submission artifact found` 해결

### 2.1 문제 현상
GitHub 푸시 후 TinyTapeout 포털에서 커밋을 검증할 때 다음 에러 발생:
> `No tt_submission artifact found for commit`

### 2.2 원인 분석
1. **GitHub Actions 실패**:
   `.github/workflows/gds.yaml` 워크플로우의 첫 번째 스텝인 `checkout repo`가 즉시 실패(Failure)하여 아티팩트 발행 스텝(`Create and publish the GDS artifact`)이 실행되지 못함.
2. **Git Submodule 엔트리 오류**:
   - 로컬 작업공간의 `tt/` 디렉터리(지원 도구 폴더)가 `.git`을 포함하고 있어 Git index에 mode `160000`(서브모듈 링크)으로 등록되어 있었음.
   - 그러나 루트에 서브모듈 URL을 정의하는 `.gitmodules` 파일이 존재하지 않았음.
   - GitHub Actions의 `actions/checkout@v4`가 `submodules: recursive` 설정에 따라 서브모듈을 복제하려다 `No url found for submodule path 'tt' in .gitmodules` 에러를 발생시킴.

### 2.3 해결 내용
1. **Git Index에서 깨진 Submodule 엔트리 제거**:
   ```bash
   git rm --cached tt
   ```
2. **`.gitignore`에 `tt/` 추가**:
   - `.gitignore`의 도구/PDK 섹션에 `tt/`를 추가하여 향후 서브모듈로 재등록되는 현상 방지.
3. **커밋 및 푸시**:
   - 커밋 메시지: `fix(ci): remove untracked git submodule entry tt causing checkout failure`
   - 메인 브랜치로 푸시 완료.

---

## 3. 최종 검증 결과

GitHub Actions `gds` 워크플로우([Run #31766394368](https://github.com/wecallemjazzyfact/TinyTapeout-BGR-LDO/actions/runs/31766394368)) 결과:

| 단계 / 잡 | 상태 | 세부 내용 |
| :--- | :---: | :--- |
| `checkout repo` | **Success** | Submodule checkout 정상 통과 |
| `Read top module name` | **Success** | `tt_um_wecallemjazzyfact_bgr_ldo` 정상 파싱 |
| `Create and publish GDS artifact` | **Success** | **`tt_submission` 아티팩트 생성 완료 (346.7 KB)** |
| `gds_render` | **Success** | GDS 렌더링 이미지 아티팩트 생성 (85.1 KB) |

---

## 4. 참고 사항 (향후 제출 시 주의점)
- **Top Module Name 고유성**: 항상 `tt_um_<github_username>_<project>` 형식을 유지합니다.
- **산출물 동기화**: `info.yaml`, `src/project.v`, `gds/*.gds`, `lef/*.lef`의 모듈 이름은 모두 일치해야 합니다.
- **Git Submodule 관리**: 서브모듈을 사용할 계획이 없다면 저장소 내 하위 폴더의 `.git`이 index에 submodule로 add되지 않도록 항상 주의합니다.
