# Review độc lập ZER-48 — offline package

Reviewer /root/zer48_review, read-only theo expert-lens pass gitnexus-review; base/head0b72eddff03e86fea0d19ac593da34c59479aaaa, branch codex/zer-48-llm-adapter,5file source/CI uncommitted. Không review unrelated dirty work, không provider/lab/publication.

**Final verdict: READY for the frozen offline package. No remaining actionable findings.** Final hashes ở [source-hashes.json](source-hashes.json), khớp live files khi reviewer đọc. Đây không là human approval, inference thật hay Done.

| Finding | Tái hiện trước sửa | Fix và retest |
| --- | --- | --- |
| MEDIUM: retry backoff bỏ qua shared run deadline |run0.05s + backoff0.5s: trả sau0.500s/1request. |min(call_remaining,budget.remaining()) trước sleep; probe trả ngay/1dispatch; deterministic regression đạt. |
| MEDIUM: JSON exponent overflow |closed Pydantic model value:float nhận1e999→inf và adapterOK. |strict parse_float finite; SCHEMA_INVALID, None,1attempt, usage100 vẫn accounted. |
| MEDIUM: H-key guard trước JSON normalization |observation items là tuple chứa cause, canonical thành list rồi đi qua request, adapterOK. |recheck forbidden_keys sau canonical normalization, chặn trước reservation/dispatch; regression và probe đạt. |

Reviewer độc lập chạy lại22focused tests bằng production-nemesis Python:PASS. Root chạy22case trên cả hai pin. Review resource ownership/cancel, retry/fatal, concurrent accounting, input/output closure, trace filtering, helper and CI imports không còn actionable defect. Simplicity: helper nhỏ/shared module, không agent framework, không đổi consumer/guard.

Một root regression pending deadline từng phụ thuộc Windows timer; thay bằng clock mô phỏng hết run trong pending fake, không đổi production cap. Reviewer đã kiểm delta này. Trước-sau test logs và mô tả sai lệch capture giữ ở verification/README.

Fresh graph/PDG/taint không có: index cũ không map source mới; không dùng zero hits làm proof. Authenticated recorder delivery và Nemesis runtime packaging là caller integration riêng. Inference thật qua adapter mới và publication/Hoàng acceptance vẫn còn.

## Actual adapter inference evidence review — 28/10/2026

Same reviewer independently replayed the recorded provider response offline through Adapter._parse/HealthSummary; no new request. Actual reply status/model/schema/expected result, context/decision/call/event/config/prompt joins, request973bytes, reservation2253tokens/0.0003277USD, observed162+22tokens/0.0000272USD estimate,1attempt/4.625s and source5pins match. Proposal bytescopy/hash and human authorization verified. Original capture SHA d669d6e4e6d3caa4cf35992b22bf057ea2d2901f93da2eb6baeea275c2a36aee remains in scratch; published receipt only normalizes CRLF to LF as declared in live-capture.json. No raw error/token/header leak found. Metadata publication review pending final signal; CI/merge/Done not yet.

## Final publication readiness

Reviewer /root/zer48_review: READY_FOR_PUBLICATION, no actionable findings. Actual provider output and all trace/source/config/prompt joins checked; human authorization and approved proposal bytes verified. All32 manifest entries matched at review. Original vs published live receipt differs only declared CRLF to LF and parsed bodies identical. Current metadata correctly distinguishes historical checkpoints; no credential leakage. Zero new provider/lab requests during review. TechnicalAC01 is satisfied at shared-adapter scope; proceed only through remaining CI/review/merge and owner conditional acceptance. No deployed consumers/G3/G4/end-to-end claim.
