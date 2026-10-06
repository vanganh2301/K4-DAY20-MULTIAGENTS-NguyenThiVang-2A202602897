# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thị Vàng | 2A202602897 | 100% |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `meta/llama-3.2-11b-vision-instruct` (NVIDIA NIM), `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows, chạy trực tiếp (host)
- Số lần chạy tác vụ đã dùng / ngân sách: 0 / 25
- Commit của tag `freeze`:

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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
