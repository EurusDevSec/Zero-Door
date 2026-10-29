# Publication ZER-19

Hoàng đã duyệt runtime04 và publication có điều kiện qua call_b4c2b024a7fe4e4a99ddb44ce9a5136c. Runtime04 technical PASS/cleanup CLEAN và review độc lập READY_FOR_SCOPED_PUBLICATION; điều kiện bắt đầu publication đã đạt. Không cần thêm approval cho các bước đã duyệt.

Base HEAD093e924000861da3096185427994d9ea736df36d, default branch main (GitHub read-back); current branch codex/zer-19-nemesis-session. PrimaryR và dirty ngoài scope giữ nguyên.

Allowlist code9paths: agent-orchestrator/nemesis/session.py, session_cli.py, Dockerfile; tests/test_nemesis_session.py, tests/test_nemesis_session_io.py; infrastructure/scripts/verify-nemesis-session.sh, infrastructure/scripts/setup-phase3.sh; rebuild-nemesis.sh; .github/workflows/ci.yml. Evidence docs/evidence/ZER-19/**. Chỉ stage prefix ZER19 mới của NOW.md và milestone note trên HEADbase; không stage lịch sử dirty của ZER16/17/18/R3-G3/R4 queue/ZER48. Exact stage manifest sẽ được ghi trước commit.

Product code9pins/review trước giữ nguyên;132Python+37Bash lượt kiểm sản phẩm đã đạt,44helper checks offline đạt. Runtime04:1inference/216+26tokens/0.0000346USDestimate,1benign executor send/3HTTP200/1TCPdenied,MAX_ROUNDS1,cleanupCLEAN. Raw01–03 giữ NOT_MET/UNKNOWN lịch sử; không biến chúng thành PASS.

Commit/push đúng allowlist → PR → CI/review exact head → merge → xác minh merge tree +ownerconditionalacceptance → Linear AC01/02/03/Done readback. Không bypass required check hoặc merge khi còn lỗi chặn; sửa confirmed CI blocker trong scope và kiểm lại hành vi ảnh hưởng. Không lab/deploy/model/issue khác. Full technical evidence: runtime-04/README.md.

Metadata publication: thêm .gitattributes chỉ cho docs/evidence/ZER-19/**, theo pattern ZER46 để giữ nguyên CRLF/raw/source snapshot hashes. Không sửa raw để qua whitespace; context whitespace trong archived patch/text/log được giữ nguyên. Kiểm Git blob SHA256 so với evidence manifest trước commit.
