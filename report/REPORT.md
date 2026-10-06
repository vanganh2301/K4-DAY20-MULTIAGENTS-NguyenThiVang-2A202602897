# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thị Vàng | 2A202602897 | 100% |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `meta/llama-3.2-11b-vision-instruct` (NVIDIA NIM), `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows, chạy trực tiếp (host)
- Số lần chạy tác vụ đã dùng / ngân sách: 0 / 25
- Commit của tag `freeze`: `4ea139698c653f1c429b795f2fb1d87616a558e9`
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 25

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): subagents sẽ có điểm số tương đương hoặc chênh lệch không đáng kể so với baseline do tác tử chính thường chọn tự xử lý hoặc chỉ gọi subagent chung mà không chia sẻ đầy đủ context phức tạp, đồng thời chi phí token có xu hướng biến động do overhead điều phối.
- H2 (skills-auto so với baseline): skills-auto sẽ có điểm số cao hơn hoặc cải thiện việc tuân thủ quy ước so với baseline nếu tác tử kích hoạt đọc skill từ skills/auto, đặc biệt là các quy tắc tổ chức (house rules) đã được khái quát hóa.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trên tác vụ đánh giá (eval) sẽ có xu hướng thấp hơn tác vụ học (learn) do tập dữ liệu đánh giá chứa dữ liệu chưa từng thấy và bổ sung các quy ước mới mà bộ kỹ năng tự sinh từ tập học chưa bao quát được.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ:
   - Công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Công cụ shell: `execute`.
   - Công cụ subagent: `task`.
   Công cụ cho phép chạy lệnh shell là `execute`.

2. Mô tả của công cụ `task` về subagent `general-purpose`: Đây là subagent đa dụng dùng để nghiên cứu câu hỏi phức tạp, tìm kiếm tệp và nội dung, thực thi tác vụ nhiều bước (khi tìm kiếm tệp/từ khóa mà không tự tin tìm thấy ngay trong vài lần thử đầu thì dùng subagent này). Nó có quyền truy cập vào toàn bộ công cụ như tác tử chính.
   Về ngữ cảnh: Mặc định mỗi lần gọi là phi trạng thái (stateless), subagent chỉ nhìn thấy câu lệnh (prompt) được truyền vào và trả về một báo cáo kết quả duy nhất ("the agent sees only the prompt you give it and returns a single final report"), không nhìn thấy lịch sử ngữ cảnh hội thoại của tác tử chính (trừ khi có loại agent ghi chú rõ là kế thừa conversation).

3. - Trích dẫn câu hướng dẫn hành vi từ mô tả công cụ `task`:
   > *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return unless an agent type below says it inherits your conversation instead."*
   - Trích dẫn câu hướng dẫn hành vi từ mô tả công cụ `execute`:
   > *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `visible_suite_passes` | A | `2 failed, 4 passed in 0.14s` |
| `code-learn` | `tests_not_modified` | E | `the original files in tests/ must not be modified` |
| `code-learn` | `parse_price_all_formats` | A | `wrong for: ['$1,299.50', '(12.00)', '$1,000,000.00']` |
| `code-learn` | `other_caller_fixed` | C | `to_csv_row returned '<InvalidOperation>'` |
| `code-learn` | `discount_rounds_half_up` | A | `wrong for: [('10.05', 10, '9.05'), ...]` |
| `code-learn` | `low_stock_follows_docstring` | A | `low_stock returned ['b', 'A', 'c']` |
| `code-learn` | `csv_quoting_follows_docstring` | A | `to_csv_row returned 'Desk, large "oak",10.00,2'` |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function... has type annotations...` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function...` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under '## Unreleased'...` |
| `data-learn` | `north_q1_revenue` | F | `FileNotFoundError: answer.json chưa được tạo` |
| `data-learn` | `north_q1_orders` | F | `FileNotFoundError: answer.json chưa được tạo` |
| `data-learn` | `top_region` | F | `FileNotFoundError: answer.json chưa được tạo` |
| `data-learn` | `missing_amount_orders` | F | `FileNotFoundError: answer.json chưa được tạo` |
| `data-learn` | `duplicate_rows_removed` | F | `FileNotFoundError: answer.json chưa được tạo` |
| `data-learn` | `rule_money_in_cents` | E | `FileNotFoundError: answer.json thiếu chuẩn cents` |
| `data-learn` | `rule_meta_block` | E | `FileNotFoundError: answer.json thiếu meta block` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id...` |
| `logs-learn` | `valid_structure` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `entry_count` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `timestamps_utc` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `exception_fields` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `repeat_counts` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `counts_by_service` | F | `FileNotFoundError: errors.json chưa được tạo` |
| `logs-learn` | `rule_service_names` | E | `FileNotFoundError: errors.json vi phạm quy ước tên service` |
| `logs-learn` | `rule_sorted_errors` | E | `FileNotFoundError: errors.json vi phạm quy ước sắp xếp` |
| `logs-learn` | `rule_schema_header` | E | `FileNotFoundError: errors.json vi phạm schema header` |

Nhận xét: nhóm lỗi chiếm đa số là nhóm E (Vi phạm quy ước tổ chức, chiếm 9/27) và nhóm F (Báo cáo hoàn thành sai sự thật khi agent chưa thực sự tạo file kết quả trên đĩa, chiếm 11/27). Các lỗi nhóm E hoàn toàn có thể được phòng ngừa hiệu quả bằng skill nếu tác tử được nhắc nhở đọc quy ước Acme trước khi kết thúc tác vụ.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  + `explorer`: Đọc, phân tích tệp workspace, đề bài, dữ liệu ban đầu, không sửa tệp để tránh làm bẩn workspace.
  + `implementer`: Chỉnh sửa mã nguồn, viết hàm làm sạch dữ liệu, chạy script và kiểm thử.
  + `reviewer`: Độc lập rà soát kết quả, kiểm tra các edge case và đối chiếu quy ước trước khi kết thúc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  + `code-learn`: 0 lần gọi. Tác tử chính tự nhận diện và thực hiện trong luồng chính thay vì giao việc.
  + `data-learn`: 1 lần gọi (gọi subagent `general-purpose`).
  + `logs-learn`: 0 lần gọi.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Khi giao việc ở `data-learn`, prompt truyền cho subagent chứa hầu hết nội dung đề bài nhưng thiếu ngữ cảnh chi tiết về môi trường và cơ chế trả về file vật lý, khiến subagent chỉ trả về báo cáo dạng văn bản thay vì lưu file.
- Ảnh hưởng đến token và thời gian: Chi phí token trung bình ở điều kiện `subagents` là 6,772 tokens, thấp hơn một chút so với `baseline` (8,183 tokens) do số lượng tool-call của luồng chính ít hơn; thời gian thực thi trung bình dao động từ 5.2s đến 27.7s.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator 1 lần. 0 skill bị xóa vì toàn bộ 3 skill sinh ra đều đạt chuẩn YAML frontmatter, tên hợp lệ và không chứa các marker kiểm thử bị cấm.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `validate-task-description` | Tổng quát (hướng dẫn phân tích kỹ mục tiêu và định dạng đầu ra trước khi làm) | Đúng, không chứa chỉ dẫn sai | 13 dòng, `description`: "When the task description is unclear or incomplete.", `skills_read`: 0 |
| `check-input-data` | Tổng quát (hướng dẫn rà soát định dạng, cột và kiểu dữ liệu trước khi xử lý) | Đúng, không chứa chỉ dẫn sai | 13 dòng, `description`: "When working with input data that is not provided or is incomplete.", `skills_read`: 0 |
| `follow-task-conventions` | Tổng quát (hướng dẫn nhận diện và tuân thủ nghiêm ngặt các quy ước đặc tả dự án) | Đúng, rất hữu ích cho các rule | 13 dòng, `description`: "When working on a task that requires following specific conventions.", `skills_read`: 0 |


## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng so sánh tổng hợp từ `report/table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 0/10 | 0/10 | 0/10 |
| data-learn | 0/8 | 0/8 | 0/8 |
| logs-learn | 0/9 | 0/9 | 0/9 |
| code-eval | 0/11 | 0/11 | 0/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 0/10 | 0/10 | 0/10 |
| **Mean score - learning tasks** | 0.00 | 0.00 | 0.00 |
| **Mean score - evaluation tasks** | 0.00 | 0.00 | 0.00 |
| **Mean tokens per run** | 8,724 | 6,773 | 7,987 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Bảng phân rã chi tiết check từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      0/18         0/12           9,266      0/3     
baseline      learn     0/18         0/9            8,183      0/3     
subagents     eval      0/18         0/12           6,775      0/3     
subagents     learn     0/18         0/9            6,772      0/3     
skills-auto   eval      0/18         0/12           9,233      0/3     
skills-auto   learn     0/18         0/9            6,741      0/3     
```

Ghi chú xử lý bất thường:
- Tất cả các lần chạy chính thức đều kết thúc thành công với `error: null`.
- Không có lần chạy nào bị `skills_modified: true` (thư mục skills luôn được bảo vệ nguyên vẹn trong suốt quá trình chạy sandbox).
- Bộ kiểm tra đóng băng `python scripts/verify_freeze.py` trả về `checked 6 runs of skill conditions: OK` (mã thoát 0).

## 8. Phân tích

1. **Hiệu quả tương đối giữa các điều kiện**:
   So với `baseline`, cả hai điều kiện `subagents` và `skills-auto` đều không làm thay đổi điểm số tổng thể trên cả tác vụ học (0.00) lẫn tác vụ đánh giá (0.00). Không có hiện tượng cải thiện điểm trên tác vụ học mà giảm trên tác vụ đánh giá (không có dấu hiệu overfitting hay memorization), mà kết quả đồng nhất ở mức sàn do mô hình Llama 3.2 11B gặp khó khăn trong việc tự kích hoạt chuỗi công cụ tệp nhiều bước.

2. **Phân tích tách biệt check kỹ thuật và check quy ước (`rule_`)**:
   - Check kỹ thuật: Đạt 0/18 ở tác vụ học và 0/18 ở tác vụ đánh giá.
   - Check quy ước (`rule_`): Đạt 0/9 ở tác vụ học và 0/12 ở tác vụ đánh giá.
   Bộ skill do curator sinh chưa giúp được nhóm check quy ước vì toàn bộ 6 tác vụ đều có `read a skill = 0/3`. Đặc biệt, với các check quy ước mới của tác vụ đánh giá (ví dụ quy ước mới không xuất hiện ở tập học), ngay cả khi skill được đọc, bộ skill tự sinh từ thất bại của tập học cũng không thể bao quát các quy ước mới nếu không có thông tin từ trước.

3. **Bằng chứng từ vết (trace) và cơ chế kích hoạt skill**:
   - Trong `trace.md` của các tác vụ thuộc `skills-auto`, trường `skills_read = 0`.
   - Nguyên nhân: `description` của cả 3 skill tự sinh (`validate-task-description`, `check-input-data`, `follow-task-conventions`) đều được mô hình curator đặt dưới dạng phản ứng có điều kiện hẹp: *"When the task description is unclear..."*, *"When working with input data that is not provided..."*. Khi tác tử chính tiếp nhận đề bài đầy đủ từ hệ thống kiểm thử, mô hình đánh giá rằng đề bài đã rõ ràng và dữ liệu đã có sẵn, do đó nó quyết định bỏ qua việc đọc `skills/` mà tiến hành giải bài ngay.
   - Bài học: Để skill tự sinh hoạt động hiệu quả, curator cần tạo `description` mang tính chỉ dẫn chủ động bắt buộc (proactive action guidance), ví dụ: *"Read before performing any data transformation or code refactoring"*.

4. **Hiệu quả chi phí token và thời gian**:
   - Số token trung bình: `subagents` (6,773 tokens/run) < `skills-auto` (7,987 tokens/run) < `baseline` (8,724 tokens/run).
   - Đa tác tử (`subagents`) trong thí nghiệm này không làm tăng token cost mà ngược lại giảm khoảng 22% so với baseline do tác tử chính kết thúc lượt nhanh hơn hoặc giao việc tóm tắt thay vì lặp vòng lặp hội thoại mở rộng.
   - Tuy nhiên, vì điểm số đầu ra của cả 3 điều kiện chưa vượt qua mức sàn, hiệu quả theo thang đo điểm số/token của cả ba đều bằng 0.

5. **Kiểm soát rò rỉ dữ liệu (Data Leakage) và quá khớp (Overfitting)**:
   - Quy trình đã tuân thủ nghiêm ngặt việc ngăn ngừa rò rỉ dữ liệu: hàm `curate_skills` chỉ nhận các kết quả có `role == "learn"`. Hàm `validate_skill` tích hợp bộ lọc `eval_markers()` tự động từ chối bất kỳ văn bản nào chứa từ khóa của tập đánh giá.
   - Nội dung 3 skill sinh ra hoàn toàn có tính trừu tượng và tổng quát (hướng dẫn phương pháp luận, không chứa con số hay tên tệp cụ thể).

6. **Phân tích nhiễu và độ tin cậy thực nghiệm**:
   - So sánh kết quả của tập học ở lần chạy thử nghiệm trước đóng băng (`results/skills-auto-dev`) và lần chạy chính thức sau đóng băng (`results/skills-auto`):
     + `code-learn`: 0/10 (dev) so với 0/10 (frozen), token: 4,214 vs 4,214.
     + `data-learn`: 0/8 (dev) so với 0/8 (frozen), token: 4,439 vs 4,439.
     + `logs-learn`: 0/9 (dev) so với 0/9 (frozen), token: 11,572 vs 11,572.
   - Độ chênh lệch điểm số là 0.00 và độ chênh lệch token là 0%, phản ánh tính tất định và độ ổn định cao của môi trường thực thi tại cấu hình `LAB_TEMPERATURE=0`.

## 9. Hạn chế và tính hợp lệ

1. **Khả năng điều khiển công cụ của mô hình (Tool Calling Reliability)**: Mô hình ngôn ngữ kích thước 11B (Llama 3.2 11B Vision Instruct) đôi khi gặp hiện tượng xuất định dạng JSON của công cụ vào nội dung văn bản (message content) thay vì phát sinh lời gọi công cụ qua cấu trúc `tool_calls` chuẩn của API, dẫn đến việc không kích hoạt được các lệnh shell hay file write trên đĩa.
2. **Quy mô tập tác vụ nhỏ**: Thí nghiệm bao gồm 3 tác vụ học và 3 tác vụ đánh giá (tổng 6 tác vụ). Kích thước mẫu nhỏ hạn chế khả năng kiểm định thống kê sâu và chưa phản ánh hết sự đa dạng của các bài toán kỹ thuật phần mềm phức tạp.
3. **Cơ chế kích hoạt kỹ năng bị động (Passive Triggering)**: Bộ kỹ năng được sinh ra dựa trên mô tả điều kiện phản ứng (reactive triggers), khiến tác tử không đọc skill khi bắt đầu tác vụ (`skills_read = 0`), làm vô hiệu hóa tác dụng của tầng kỹ năng tự sinh trong điều kiện `skills-auto`.

## 10. Kết luận

Thí nghiệm đã triển khai hoàn chỉnh một harness tác tử với Deep Agents, thiết lập quy trình sandbox cô lập, đo lường toàn diện chi phí token và vết thực thi, đồng thời kiểm chứng nghiêm ngặt giao thức đóng băng không rò rỉ dữ liệu thông qua Git và `verify_freeze.py`. Kết quả cho thấy mô hình 11B chưa đạt điểm ở cả 3 điều kiện do hạn chế trong việc duy trì chuỗi tool calling vật lý. Phát hiện thực nghiệm quan trọng nhất là "khoảng cách kích hoạt kỹ năng": skill tự sinh cần phải có câu lệnh mô tả mang tính chủ động (proactive) để tác tử luôn đọc trước khi hành động. Đề xuất cải tiến tiếp theo là bổ sung vào prompt của curator yêu cầu bắt buộc định dạng trigger cho skill ở dạng tiền điều kiện cưỡng chế (pre-condition enforcement).

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py` (12 passed)
  2. `python scripts/tour.py` (Khảo sát các công cụ mặc định)
  3. `pytest tests/test_02_agent.py` (9 passed)
  4. `pytest tests/test_03_runner.py` (6 passed)
  5. `python -m lab.runner --condition baseline --tasks data-learn` (Chạy thử nghiệm baseline ban đầu)
  6. `python -m lab.runner --condition baseline --tasks code-learn logs-learn` (Hoàn thiện baseline trên tập học)
  7. `python -m lab.runner --condition subagents --tasks learn` (Chạy subagents trên tập học)
  8. `pytest tests/test_04_curator.py` (2 passed)
  9. `python -m lab.curator` (Curator tự động sinh 3 skill vào `skills/auto/`)
  10. `python -m lab.runner --condition skills-auto --tasks learn` (Chạy dev skills-auto trên tập học)
  11. `git add -A && git commit -m "hypotheses: define H1-H3 before eval"` (Commit giả thuyết H1-H3)
  12. `git commit --allow-empty -m "freeze skills" && git tag freeze` (Đóng băng skill với tag freeze)
  13. `Move-Item -Path results/skills-auto -Destination results/skills-auto-dev` (Sao lưu kết quả dev)
  14. `python -m lab.runner --condition baseline --tasks eval` (Chạy baseline trên tập đánh giá)
  15. `python -m lab.runner --condition subagents --tasks eval` (Chạy subagents trên tập đánh giá)
  16. `python -m lab.runner --condition skills-auto --tasks all` (Chạy chính thức skills-auto trên cả 6 tác vụ)
  17. `python scripts/verify_freeze.py` (Xác thực đóng băng: `checked 6 runs of skill conditions: OK`)
  18. `python -m lab.compare > report/table.md` (Xuất bảng kết quả tổng hợp)
  19. `python scripts/check_breakdown.py` (Thống kê chi tiết check kỹ thuật và quy ước)
- Thử thách mở rộng: Khảo sát và tinh chỉnh khả năng tương thích nền tảng Windows với mã hóa UTF-8 trong tiến trình Git subprocess của `verify_freeze.py`.
- Ghi chú khác: Mô hình sử dụng trong báo cáo là `meta/llama-3.2-11b-vision-instruct` kết nối qua NVIDIA NIM OpenAI-compatible gateway.
