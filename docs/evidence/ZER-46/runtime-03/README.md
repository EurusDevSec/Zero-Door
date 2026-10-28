# ZER-46 runtime-03 — RAM/PSI đạt, dừng trước fixture vì Boutique timeout

**NOT_MET / COMPONENT_NOT_STARTED / NOT_READY_FOR_PUBLICATION.** Hoàng đã báo RAM được giải phóng và gói cache+retry có quyền. Lượt kết thúc sau147,90s, không tự retry.

Independent-verification.json đối chiếu raw, không dùng PASS string:28mẫu guard, preflight span119,993s theo25sample lịch120s; host min3,95GiB, WSL min2,42GiB, memoryPSI0. Hai image đúng digest đã pull thành công/có cache. Không fixturebuild/import, Kubernetesresourcewrite, namespace, policy, worker hay fixtureHTTP.

Boutique có9HTTP qua3flow: warmup home timeout3012,23ms (0pacing); readback product timeout và checkout timeout. Các walltime4285,04/7621,69ms giữ nguyên cùng pacing500/3000ms; không relabel thànhhealthy/KPI. Flow báo cartcleanupDONE, không có GET độc lập kiểm cartempty trong lượt này. Sharedspec/UID/restart và3PVC giữ nguyên, namespaceabsent. Ownresourcecleanup không có actor mới; overalllabreadbackINCOMPLETE vìbusinesskhôngkhỏe.

Nguyên nhân Boutique chưa được xác định; không quy lỗi cho RAM, SQLi hay BLOCK_IP vì component chưa bắt đầu. Rawfailure/acceptance/cleanup giữ nguyên. Runtime03 không sửa DNS/CPU/Ingress/CNI, restart app/node/cluster, Kafka/model hoặc publication.

Hoàng sau đó duyệt gói fixture-only-proposal.md: protectedfixturebaseline phải đạt; Boutique vẫn đo trước/sau nhưng lỗi sẵn có không là admissiongate của component. Approval mới không biến Boutique/R1/KPI thànhPASS. Runtime04 có scope/receipt riêng, không thay verdict lượt này.
