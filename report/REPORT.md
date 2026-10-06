# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thị Vàng | 2A202602897 | Cài đặt harness (agent, subagents, runner, curator); Thực nghiệm toàn bộ 3 điều kiện (baseline, subagents, skills-auto); Phân loại lỗi và chẩn đoán căn nguyên; Thực hiện quy trình đóng băng kỹ năng (freeze protocol); Tổng hợp bảng so sánh và phân tích, hoàn thiện toàn bộ báo cáo (Mục 1–10) |

- Mô hình: `meta/llama-3.2-11b-vision-instruct` (NVIDIA NIM OpenAI-compatible gateway: `https://integrate.api.nvidia.com/v1`)
- Nhiệt độ (`LAB_TEMPERATURE`): `0`
- `recursion_limit`: `60`
- Phiên bản Deep Agents: `deepagents 0.7.21` (`pip show deepagents`)
- Hệ điều hành: Windows 11 (Host machine, Python 3.11.9)
- Ngân sách và số lần chạy tác vụ: 21 / 25 runs đã dùng
- Git commit của giả thuyết H1-H3: `5b629cb` (`hypotheses: define H1-H3 before eval`)
- Git commit của tag `freeze`: `4ea1396` (`freeze skills`)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): subagents sẽ có điểm số tương đương hoặc chênh lệch không đáng kể so với baseline do tác tử chính thường chọn tự xử lý hoặc chỉ gọi subagent chung mà không chia sẻ đầy đủ context phức tạp, đồng thời chi phí token có xu hướng biến động do overhead điều phối.
  - *Căn cứ lý thuyết*: Theo tài liệu nghiên cứu của Anthropic (2024, "Building Effective Agents") và Hong et al. (2023, "MetaGPT"), việc phân rã đa tác tử không có trạng thái chia sẻ (stateless delegation) thường tạo ra chi phí điều phối (coordination overhead) và rủi ro mất mát ngữ cảnh giữa các tác tử, khiến tỷ lệ hoàn thành tác vụ không nhất thiết cao hơn kiến trúc đơn tác tử nếu không có giao thức trao đổi dữ liệu có cấu trúc.
- H2 (skills-auto so với baseline): skills-auto sẽ có điểm số cao hơn hoặc cải thiện việc tuân thủ quy ước so với baseline nếu tác tử kích hoạt đọc skill từ skills/auto, đặc biệt là các quy tắc tổ chức (house rules) đã được khái quát hóa.
  - *Căn cứ lý thuyết*: Theo Wang et al. (2023, "Voyager: An Open-Ended Embodied Agent") và Shinn et al. (2023, "Reflexion"), việc lưu trữ các kỹ năng và bài học phản tư vào bộ nhớ ngoài (procedural memory) giúp tác tử tích lũy kinh nghiệm giải quyết các lỗi lặp lại. Đồng thời, tài liệu đặc tả của LangChain Deep Agents về cơ chế Progressive Disclosure khẳng định việc nạp các kỹ năng dạng checklist hỗ trợ định hướng hành vi tuân thủ quy tắc tổ chức tốt hơn bộ hướng dẫn tĩnh.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trên tác vụ đánh giá (eval) sẽ có xu hướng thấp hơn tác vụ học (learn) do tập dữ liệu đánh giá chứa dữ liệu chưa từng thấy và bổ sung các quy ước mới mà bộ kỹ năng tự sinh từ tập học chưa bao quát được.
  - *Căn cứ lý thuyết*: Dựa trên nguyên lý tổng quát hóa ngoài phân phối (out-of-distribution generalization) trong các hệ thống LLM-agent (Zhou et al., 2023, "WebArena"), các quy ước ẩn mới (novel house rules) không xuất hiện trong tập huấn luyện/tập học sẽ không thể được giải quyết bằng các kỹ năng tĩnh tự sinh nếu thiếu cơ chế suy luận ngoại suy tại thời điểm chạy.

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

### Bảng phân loại lỗi trên các tác vụ học (Baseline Learning Tasks)

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
| `data-learn` | `north_q1_revenue` | F | `FileNotFoundError: workspace/answer.json` (agent khẳng định hoàn tất nhưng file không tồn tại trên đĩa) |
| `data-learn` | `north_q1_orders` | F | `FileNotFoundError: workspace/answer.json` (agent khẳng định hoàn tất nhưng file không tồn tại trên đĩa) |
| `data-learn` | `top_region` | F | `FileNotFoundError: workspace/answer.json` (agent khẳng định hoàn tất nhưng file không tồn tại trên đĩa) |
| `data-learn` | `missing_amount_orders` | F | `FileNotFoundError: workspace/answer.json` (agent khẳng định hoàn tất nhưng file không tồn tại trên đĩa) |
| `data-learn` | `duplicate_rows_removed` | F | `FileNotFoundError: workspace/answer.json` (agent khẳng định hoàn tất nhưng file không tồn tại trên đĩa) |
| `data-learn` | `rule_money_in_cents` | E | `RULE: revenue and money amounts must be in cents` (gãy trước khi ghi nhận định dạng) |
| `data-learn` | `rule_meta_block` | E | `RULE: include metadata header block` (gãy trước khi ghi nhận định dạng) |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv` (gãy trước khi ghi nhận tệp) |
| `logs-learn` | `valid_structure` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `entry_count` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `timestamps_utc` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `exception_fields` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `repeat_counts` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `counts_by_service` | F | `FileNotFoundError: workspace/errors.json` (agent khẳng định đã xuất kết quả nhưng file vắng mặt) |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in errors.json must be lowercase` (gãy trước khi ghi nhận tệp) |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors must be sorted by timestamp` (gãy trước khi ghi nhận tệp) |
| `logs-learn` | `rule_schema_header` | E | `RULE: include schema version header` (gãy trước khi ghi nhận tệp) |

### Nhận xét phân bố nhóm lỗi theo Rubric

- **Nhóm lỗi chiếm đa số**: Phân bố lỗi quan sát được (observed agent failures) tập trung chủ yếu vào hai nhóm:
  1. **Nhóm F (Báo cáo hoàn thành sai sự thật / không tạo tệp kết quả như tuyên bố)**: Chiếm 11/27 check thất bại (40.7%), xảy ra ở toàn bộ các check kỹ thuật của `data-learn` và `logs-learn`. Trong trace, tác tử tuyên bố đã phân tích và lưu kết quả, nhưng thực tế `workspace/answer.json` và `workspace/errors.json` không hiện diện trên đĩa.
  2. **Nhóm E (Vi phạm quy ước tổ chức ngầm `rule_`)**: Chiếm 9/27 check thất bại (33.3%), trải đều trên cả 3 tác vụ. Đây là các quy ước đặc thù của tổ chức không hề được nêu trong đề bài.
  3. **Nhóm A (Bỏ qua đặc tả)**: Chiếm 6/27 check (22.2%), tập trung ở `code-learn` khi mô hình không bám sát docstring về cách xử lý rounding, chuỗi CSV và định dạng giá.
  4. **Nhóm C (Vá triệu chứng)**: Chiếm 1/27 check (3.7%) tại `code-learn` (`other_caller_fixed`).
- **Khả năng phòng ngừa bằng Kỹ năng (Skill)**:
  - Nhóm E: Hoàn toàn có thể phòng ngừa bằng skill nếu curator phát hiện và tổng hợp các quy ước tổ chức thành checklist hướng dẫn tác tử tuân thủ.
  - Nhóm A: Có thể phòng ngừa bằng skill kiểm tra tiền điều kiện (như đọc kỹ docstring và test suite trước khi chỉnh sửa).
  - Nhóm F: Cần skill hướng dẫn tác tử bắt buộc phải thực thi lệnh kiểm tra sự tồn tại của tệp trên đĩa (`ls` hoặc `read_file`) trước khi báo cáo kết thúc.
- **Bằng chứng phủ định cho các nhóm B và D**: Bảng thống kê từ `scripts/check_breakdown.py` cho thấy các check kỹ thuật ở tác vụ học đạt 0/18. Tuy nhiên, tác tử không rơi vào nhóm B (thiếu kiểm chứng) hay nhóm D (sót dữ liệu bẩn) vì toàn bộ các bước kiểm tra dữ liệu bẩn trong log suy luận đã bị chặn lại trước khi tạo ra tệp đích.

### Ghi chú chẩn đoán căn nguyên kỹ thuật (Root-Cause Diagnostic Note)

*Lưu ý phương pháp luận theo Rubric*: Rubric quy định rõ ràng rằng *"Lỗi do hạ tầng (API lỗi, hết thời gian) không được tính là lỗi của tác tử và không dùng làm bằng chứng"*. Do đó, bảng phân loại lỗi ở trên hoàn toàn bám sát hành vi quan sát được ở cấp độ tác tử (Nhóm F và Nhóm E) và không sử dụng lỗi hạ tầng để phóng đại số liệu phân loại lỗi.

Chẩn đoán chuyên sâu về cơ chế kỹ thuật bên dưới (root-cause diagnosis) cho thấy hiện tượng tác tử không tạo tệp (Nhóm F) chịu tác động trực tiếp từ hiện tượng **Cascade Breakdown** (gãy tầng thực thi tuần hoàn giữa mô hình và framework):
1. **Năng lực Tool-calling của Endpoint**: Kiểm tra độc lập (diagnostic mini-test) xác nhận endpoint NVIDIA NIM phản hồi đúng cấu trúc `tool_calls` chuẩn OpenAI. Tuy nhiên, mô hình 11B gặp hiện tượng sai lệch đối số (argument hallucination/leakage).
2. **Cơ chế gãy tầng thực thi lồng ghép (Nested Multi-Agent Failure)**: Trong tác vụ `data-learn`, main agent gọi tool `task` thành công để ủy quyền cho subagent. Tuy nhiên, subagent bên trong không phát structured tool call cho lệnh `execute` mà lại serialize lời gọi này thành một chuỗi văn bản JSON thuần túy trong nội dung báo cáo.
3. **Lây nhiễm ngữ cảnh (Context Contamination)**: Main agent khi tiếp nhận báo cáo dạng văn bản JSON từ subagent đã bị "nhiễm" định dạng đó, dẫn đến việc ở bước cuối cùng, nó xuất lời gọi `write_file` dưới dạng text JSON kết thúc lượt thay vì phát một tool call hợp lệ.
4. **Hậu quả thực thi**: Toàn bộ run chỉ ghi nhận duy nhất 1 tool call thực sự (`task`). Không có lệnh ghi tệp nào được thực thi xuống hệ thống tệp vật lý, dẫn đến `FileNotFoundError` khi grader kiểm tra.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế)**:
  Hệ thống định nghĩa 3 subagent chuyên biệt hóa rõ ràng về vai trò trong `src/lab/subagents.py`:
  1. `explorer`: Chuyên trách đọc, phân tích tệp workspace, đề bài, dữ liệu ban đầu và dấu vết lỗi; chỉ thị hành vi ghi rõ "Do NOT modify any files" nhằm tránh làm biến đổi trạng thái workspace ban đầu.
  2. `implementer`: Chuyên trách sửa đổi mã nguồn, viết script làm sạch dữ liệu, chạy lệnh shell và kiểm thử; được chỉ định khi cần can thiệp logic hoặc chạy script thực thi.
  3. `reviewer`: Chuyên trách kiểm tra độc lập kết quả đầu ra, rà soát các edge cases và đối chiếu các quy ước trước khi kết thúc tác vụ.
- **`subagent_calls` ở từng tác vụ và nhận xét**:
  - `code-learn`: 0 lần gọi. Main agent tự xử lý toàn bộ các thao tác chỉnh sửa mã nguồn trong luồng chính vì mô hình đánh giá tác vụ có thể giải quyết trực tiếp.
  - `data-learn`: 1 lần gọi (gọi subagent `general-purpose`).
  - `logs-learn`: 0 lần gọi. Main agent tự tiến hành phân tích log mà không ủy quyền.
- **Thông tin thiếu hoặc thừa khi giao việc (ở `data-learn`)**:
  Khi giao việc cho subagent ở `data-learn`, prompt truyền vào đã bao quát các yêu cầu tính toán doanh thu nhưng thiếu chỉ dẫn bắt buộc về cơ chế tương tác tệp vật lý trong môi trường phi trạng thái (stateless). Do đó, subagent chỉ thực hiện tính toán trên bộ nhớ và trả về báo cáo dạng chuỗi văn bản thay vì ghi file vào `workspace/`.
- **Ảnh hưởng đến token và thời gian**:
  Chi phí token trung bình ở điều kiện `subagents` là 6,772 tokens/run (trên tập học) và 6,775 tokens/run (trên tập đánh giá), thấp hơn khoảng 22% so với baseline (8,183 tokens/run ở tập học). Nguyên nhân giảm token là do luồng chính dừng sớm sau khi nhận báo cáo từ subagent. Thời gian thực thi dao động từ 5.2s đến 27.7s.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator, số skill bị xóa và lý do**:
  Chạy curator 1 lần (`python -m lab.curator`). Toàn bộ 3 skill do mô hình sinh ra đều đạt chuẩn cú pháp YAML frontmatter, tên hợp lệ, không chứa ký tự cấm (`../`) và không chứa marker kiểm thử bị cấm (`eval_markers`), do đó 0 skill bị xóa.

### Đánh giá chất lượng chi tiết từng kỹ năng sinh ra (Rubric 4.2)

#### 1. Kỹ năng `validate-task-description`
- **Tính tổng quát hay quá khớp**: Hoàn toàn tổng quát (general procedural checklist). Nội dung hướng dẫn tác tử đọc kỹ mô tả, xác định mục tiêu chính, kiểm tra dữ liệu đầu vào và định dạng đầu ra mong muốn. Không chứa bất kỳ dữ kiện, tên tệp hay con số cụ thể nào của tập học.
- **Tính đúng đắn / sai lệch / gây hại**: Đúng đắn về mặt logic kỹ thuật phần mềm. Tuy nhiên, có một hạn chế nhỏ trong môi trường sandbox tự động: dòng 11 hướng dẫn *"ask the human for more information"* khi đề bài chưa rõ ràng. Trong benchmark tự động không có con người can thiệp (human-in-the-loop), việc cố hỏi con người có thể làm lãng phí lượt tương tác nếu tác tử dừng lại chờ đợi. Kỹ năng không chứa bất kỳ chỉ dẫn độc hại nào.
- **Độ dài, trigger `description` và cơ chế kích hoạt**:
  - Độ dài: 13 dòng (bao gồm YAML frontmatter).
  - `description`: `"When the task description is unclear or incomplete."`
  - Cơ chế kích hoạt: Đây là một trigger phản ứng thụ động (passive/conditional trigger). Khi tác tử chính tiếp nhận đề bài đầy đủ từ harness, mô hình tự nhận định rằng đề bài đã rõ ràng nên không kích hoạt đọc skill này (`skills_read = 0`).

#### 2. Kỹ năng `check-input-data`
- **Tính tổng quát hay quá khớp**: Hoàn toàn tổng quát. Kỹ năng tập trung vào quy trình kiểm tra dữ liệu đầu vào: xác minh định dạng dữ liệu, kiểm tra các cột/trường cần thiết, kiểu dữ liệu và yêu cầu định dạng đặc thù. Không bị overfit vào bất kỳ schema hay tên cột cụ thể nào của các bài toán học.
- **Tính đúng đắn / sai lệch / gây hại**: Đúng đắn về mặt kỹ thuật xử lý dữ liệu. Kỹ năng nhắc nhở kiểm tra kiểu dữ liệu và giá trị thiếu trước khi tính toán. Tương tự như skill trước, khuyến nghị hỏi con người ở bước 3 và 5 là phản xạ mặc định của LLM khi gặp dữ liệu thiếu. Kỹ năng không gây hại cho môi trường thực thi.
- **Độ dài, trigger `description` và cơ chế kích hoạt**:
  - Độ dài: 13 dòng (bao gồm YAML frontmatter).
  - `description`: `"When working with input data that is not provided or is incomplete."`
  - Cơ chế kích hoạt: Trigger mang tính điều kiện tiêu cực ("data is not provided or is incomplete"). Do tệp dữ liệu đầu vào (`sales.csv`, `orders.csv` hoặc log) đã hiện diện sẵn trong thư mục làm việc, tác tử không kích hoạt đọc skill (`skills_read = 0`).

#### 3. Kỹ năng `follow-task-conventions`
- **Tính tổng quát hay quá khớp**: Hoàn toàn tổng quát. Hướng dẫn tác tử rà soát các quy ước đặc tả, tài liệu hướng dẫn, code style guides và định dạng dữ liệu, đồng thời yêu cầu kiểm tra đối chiếu lại sản phẩm trước khi nộp. Kỹ năng không overfit vào các quy tắc riêng của Acme Corp (như `rule_money_in_cents` hay `rule_clean_csv`).
- **Tính đúng đắn / sai lệch / gây hại**: Hoàn toàn đúng đắn và có giá trị định hướng cao nhất trong 3 skill đối với bài toán Acme house rules. Không có bất kỳ nội dung sai lệch hay độc hại nào.
- **Độ dài, trigger `description` và cơ chế kích hoạt**:
  - Độ dài: 13 dòng (bao gồm YAML frontmatter).
  - `description`: `"When working on a task that requires following specific conventions."`
  - Cơ chế kích hoạt: Trigger phụ thuộc vào việc nhận biết "specific conventions". Vì các quy ước ngầm của tổ chức không được đề bài nhắc tên tường minh là "specific conventions", tác tử chính không nhận thức được sự cần thiết của việc tra cứu kỹ năng này, dẫn đến `skills_read = 0`.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `validate-task-description` | Tổng quát (hướng dẫn phân tích kỹ mục tiêu và định dạng đầu ra trước khi làm) | Đúng về logic; khuyến nghị hỏi human không tối ưu cho benchmark tự động | 13 dòng, `description`: "When the task description is unclear or incomplete.", `skills_read`: 0 |
| `check-input-data` | Tổng quát (hướng dẫn rà soát định dạng, cột và kiểu dữ liệu trước khi xử lý) | Đúng; khuyến nghị hỏi human là hạn chế nhỏ trong môi trường sandbox | 13 dòng, `description`: "When working with input data that is not provided or is incomplete.", `skills_read`: 0 |
| `follow-task-conventions` | Tổng quát (hướng dẫn nhận diện và tuân thủ nghiêm ngặt các quy ước đặc tả dự án) | Hoàn toàn đúng, có giá trị định hướng cao nhất cho các quy tắc tổ chức | 13 dòng, `description`: "When working on a task that requires following specific conventions.", `skills_read`: 0 |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng so sánh tổng hợp (`report/table.md` - do `python -m lab.compare` sinh ra)

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

### Bảng phân rã chi tiết check kỹ thuật và quy ước (`python scripts/check_breakdown.py`)

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      0/18         0/12           9,266      0/3     
baseline      learn     0/18         0/9            8,183      0/3     
subagents     eval      0/18         0/12           6,775      0/3     
subagents     learn     0/18         0/9            6,772      0/3     
skills-auto   eval      0/18         0/12           9,233      0/3     
skills-auto   learn     0/18         0/9            6,741      0/3     
```

### Xử lý bất thường và xác thực đóng băng

- Tất cả 18 lượt chạy chính thức đều hoàn tất với `error: null` (không có lỗi hệ thống hoặc ngoại lệ crash).
- Không có lần chạy nào vi phạm `skills_modified = true` (thư mục kỹ năng được bảo vệ nguyên vẹn trong suốt quá trình chạy sandbox).
- Quy trình đóng băng được xác thực thành công tuyệt đối qua script chuẩn:
  `python scripts/verify_freeze.py` trả về `checked 6 runs of skill conditions: OK` (mã thoát 0).

## 8. Phân tích

1. **Hiệu quả tương đối giữa các điều kiện**:
   So với `baseline`, cả hai điều kiện `subagents` và `skills-auto` đều đạt điểm số trung bình là 0.00 trên cả tác vụ học và tác vụ đánh giá. Không có điều kiện nào tạo ra sự cải thiện điểm số.
   *Đánh giá học thuật khách quan*: Kết quả kỹ thuật 0/18 không thể quy chụp hoàn toàn là do năng lực suy luận (reasoning quality) của tác tử kém, bởi quá trình thực thi bị chi phối áp đảo bởi sự cố giao tiếp mô hình - công cụ (model-tool interface bottleneck). Đồng thời, các vết thực thi (trace) cũng ghi nhận những sai sót logic ở cấp độ tác vụ (ví dụ trong `data-learn`, subagent lọc `region == 'North'` rồi lại cố gắng tìm `top_region` bằng `df.groupby('region')`). Do đó, thí nghiệm không thể phân tách độc lập hai yếu tố này.

2. **Phân tích tách biệt check kỹ thuật và check quy ước (`rule_`)**:
   - Dựa vào kết quả của `scripts/check_breakdown.py`:
     + Check kỹ thuật: 0/18 ở tập học và 0/18 ở tập đánh giá qua tất cả các điều kiện.
     + Check quy ước (`rule_`): 0/9 ở tập học và 0/12 ở tập đánh giá qua tất cả các điều kiện.
   - Kỹ năng do curator sinh chưa hỗ trợ được nhóm check quy ước vì không có lượt chạy nào kích hoạt đọc kỹ năng (`read a skill = 0/3`).
   - Đối với các quy ước mới của tác vụ đánh giá (những quy tắc chưa từng xuất hiện ở tập học), ngay cả khi kỹ năng được kích hoạt, các quy ước đặc thù mới này cũng không thể được bao quát bởi bộ kỹ năng sinh từ tập học nếu không có thêm thông tin đặc tả từ môi trường.

3. **Bằng chứng từ vết (trace) và cơ chế kích hoạt skill**:
   - Trong toàn bộ các tệp `trace.md` của điều kiện `skills-auto`, không có bất kỳ lệnh gọi `read_file` nào trỏ tới đường dẫn `skills/auto/...`, xác nhận `skills_read = 0/6`.
   - Một check điển hình mà skill không giúp: `rule_clean_csv` trong `data-learn`. Dù skill `follow-task-conventions` nhấn mạnh việc tuân thủ quy ước định dạng, nhưng vì skill không được đọc vào ngữ cảnh của tác tử, mô hình hoàn toàn không biết đến sự tồn tại của quy ước này.
   - Cơ chế cốt lõi: Pipeline tự tiến hóa đã sinh và đóng băng thành công 3 kỹ năng hợp lệ, nhưng các lượt chạy đo lường không kích hoạt chúng do câu lệnh mô tả điều kiện (description triggers) mang tính bị động (passive triggers). Do đó, thí nghiệm đo lường độ tin cậy của quy trình sinh kỹ năng (curation pipeline) chuẩn xác hơn là đo lường hiệu quả can thiệp hạ nguồn của kỹ năng.

4. **Hiệu quả chi phí token và thời gian**:
   - Chi phí token trung bình: `subagents` (6,773 tokens/run) < `skills-auto` (7,987 tokens/run) < `baseline` (8,724 tokens/run).
   - Trong thí nghiệm này, điều kiện `subagents` có chi phí token thấp hơn baseline khoảng 22% do tác tử chính kết thúc lượt sớm sau khi nhận chuỗi văn bản từ subagent.
   - *Lưu ý về tỷ số chi phí/hiệu quả*: Vì điểm số của mọi điều kiện đều bằng 0, không có điều kiện nào đạt hiệu quả điểm trên mỗi token (score per token = 0). Việc giảm token ở điều kiện `subagents` phản ánh sự gãy sớm của chuỗi hội thoại (early truncation) chứ không đại diện cho tính hiệu quả kinh tế (cost-effectiveness) trong việc giải quyết thành công bài toán.

5. **Kiểm soát rò rỉ dữ liệu (Data Leakage) và quá khớp (Overfitting)**:
   - Phòng tránh rò rỉ: Hàm `curate_skills` chỉ nhận đầu vào là các kết quả có `role == "learn"`. Hàm kiểm tra `validate_skill` tích hợp danh sách từ khóa kiểm thử đánh giá (`eval_markers`), tự động loại bỏ bất kỳ kỹ năng nào vô tình trích xuất thông tin của tập đánh giá.
   - Phòng tránh quá khớp: Cả 3 kỹ năng sinh ra đều mang tính khái quát cao về mặt phương pháp luận phần mềm, không lưu giữ các giá trị hardcoded hay tên tệp riêng biệt của tập học.

6. **Phân tích nhiễu và độ tin cậy thực nghiệm (Noise Estimation Table)**:
   Để ước lượng độ nhiễu thực nghiệm theo yêu cầu của Rubric 6.2, ta so sánh điểm số và chi phí token của các tác vụ học ở lần chạy thử nghiệm trước đóng băng (`results/skills-auto-dev` - Phần 3.4) với lần chạy chính thức sau đóng băng (`results/skills-auto`) với cùng một bộ kỹ năng tự sinh đã đóng băng:

| Tác vụ | Skills-auto Dev (Phần 3.4) | Skills-auto Chính thức (Sau Freeze) | Chênh lệch điểm (Δ) | Chênh lệch Token (Δ) |
|---|---:|---:|---:|---:|
| `code-learn` | 0/10 (4,214 tokens) | 0/10 (4,214 tokens) | 0.00 | 0 (0.0%) |
| `data-learn` | 0/8 (4,439 tokens) | 0/8 (4,439 tokens) | 0.00 | 0 (0.0%) |
| `logs-learn` | 0/9 (11,572 tokens) | 0/9 (11,572 tokens) | 0.00 | 0 (0.0%) |

   *Nhận xét về độ nhiễu*:
   Chênh lệch điểm số Δ = 0.00 và chênh lệch token Δ = 0 giữa hai lần thực thi độc lập khẳng định rằng quy trình chạy đạt tính tất định tuyệt đối tại cấu hình `LAB_TEMPERATURE=0`. Độ nhiễu thực nghiệm (run-to-run noise) bằng 0 chứng minh rằng kết quả không đổi trong bảng so sánh ở mục 7 là hoàn toàn ổn định và đáng tin cậy về mặt đo lường, không bị ảnh hưởng bởi biến động ngẫu nhiên.

## 9. Hạn chế và tính hợp lệ

1. **Điểm nghẽn giao tiếp mô hình - công cụ (Model-Interface Bottleneck)**:
   - *Mô tả*: Mô hình 11B gặp khó khăn trong việc sinh đối số tool call chính xác và dễ bị chuyển đổi sang dạng text JSON khi tiếp nhận văn bản từ subagent (Cascade Breakdown).
   - *Ảnh hưởng đến kết luận*: Thí nghiệm không thể phân tách rạch ròi giữa năng lực suy luận nghiệp vụ và lỗi giao tiếp công cụ; kết quả 0/18 kỹ thuật phản ánh sự đổ vỡ của chuỗi thực thi công cụ hơn là giới hạn của kiến trúc tự tiến hóa.
2. **Quy mô tập tác vụ nhỏ (Small Task Suite)**:
   - *Mô tả*: Thí nghiệm chỉ bao gồm 3 tác vụ học và 3 tác vụ đánh giá (tổng cộng 6 tác vụ).
   - *Ảnh hưởng đến kết luận*: Kích thước mẫu nhỏ hạn chế sức mạnh kiểm định thống kê và làm giảm tính khái quát hóa của việc so sánh thứ hạng giữa các điều kiện `baseline`, `subagents` và `skills-auto`.
3. **Mô hình duy nhất (Single Model Evaluation)**:
   - *Mô tả*: Toàn bộ nghiên cứu được thực hiện trên một mô hình mã nguồn mở duy nhất (`meta/llama-3.2-11b-vision-instruct`).
   - *Ảnh hưởng đến kết luận*: Các phát hiện về sự đổ vỡ của cơ chế gọi tool lồng ghép (nested tool calling) mang tính đặc thù cho lớp mô hình cỡ nhỏ; không thể suy rộng kết luận này sang các mô hình biên lớn hơn có năng lực tool-calling cao cấp (như Claude 3.5 Sonnet hay GPT-4o).
4. **Khoảng cách kích hoạt kỹ năng thụ động (Passive Trigger / Skill Activation Gap)**:
   - *Mô tả*: Mô tả của các kỹ năng sinh ra đều ở dạng điều kiện thụ động phản ứng, dẫn đến việc tác tử không đọc kỹ năng trong các lượt chạy chính thức (`skills_read = 0/6`).
   - *Ảnh hưởng đến kết luận*: Thí nghiệm xác thực thành công quy trình tự động sinh và đóng băng kỹ năng (curation pipeline), nhưng chưa thể đo lường tác động can thiệp (causal treatment effect) của các kỹ năng này lên hành vi giải quyết bài toán ở hạ nguồn.

## 10. Kết luận

Thí nghiệm đã hoàn thành chuẩn xác toàn bộ quy trình khoa học của lab: xây dựng harness Deep Agents, đo lường vết thực thi và token, triển khai curator tự động sinh kỹ năng, và tuân thủ nghiêm ngặt giao thức đóng băng không rò rỉ dữ liệu qua Git và `verify_freeze.py`. Kết quả điểm kỹ thuật 0/18 phản ánh sự kết hợp giữa điểm nghẽn giao tiếp công cụ (model-interface bottleneck) và các lỗi suy luận logic ở cấp độ tác vụ trong cấu trúc đa tác tử. Cơ chế tự tiến hóa đã chứng minh năng lực sinh thành công các kỹ năng tổng quát hợp lệ, nhưng để các kỹ năng này phát huy tác dụng ở hạ nguồn, cần phải khắc phục khoảng cách kích hoạt kỹ năng. Đề xuất cải tiến tiếp theo là bổ sung vào prompt của curator yêu cầu bắt buộc định dạng trigger mô tả kỹ năng dưới dạng tiền điều kiện chủ động (proactive mandatory checklist), đồng thời tích hợp bước tự kiểm tra tệp vật lý trước khi kết thúc tác vụ.

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
- Thử thách mở rộng: Khảo sát và tinh chỉnh khả năng tương thích nền tảng Windows với biến môi trường `PYTHONUTF8=1` để đảm bảo thực thi an toàn các tiến trình subprocess Git mà không cần can thiệp mã nguồn starter scripts.
- Ghi chú khác: Mô hình sử dụng trong toàn bộ báo cáo là `meta/llama-3.2-11b-vision-instruct` kết nối qua NVIDIA NIM OpenAI-compatible gateway.
