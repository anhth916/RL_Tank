# Kursk 1943 FPT Software - Quy Nhơn AI
[Vietnamese version - English update soon ...]
## Summary
* [Introduction](#Introduction)
* [Game Play](#Game-Play)
* [Game Mode](#Game-Mode)
* [Hướng dẫn chạy mã nguồn mở](#Hướng-dẫn-chạy-mã-nguồn-mở)

## Introduction
* Opensource học tăng cường của cuộc thi Kursk 1943 do Quy Nhơn AI tổ chức được Ban tổ chức cung cấp cho các đội chơi để hiểu thêm về kiến trúc, flow xử lý, phương thức giao tiếp giữa người chơi và môi trường game.
* Opensource sử dụng thuật toán học tăng cường Deep Q Learning tuy nhiên BTC không yêu cầu các đội buộc phải sử dụng thuật toán học tăng cường mà các đội hoàn toàn có thể sử dụng các thuật toán khác để tham gia cuộc thi này.

<p align="center">
<img src="./img/poster.jpg" alt="Poster" width="640" height="360"/>
</p>

## Game Play
* Luật chơi rất đơn giản, tiêu diệt xe tăng địch và dành chiến thắng. 
* Trong bản đồ có nhiều công trình kiên cố như nhà, boong-ke, tảng đá, vì thế hãy di chuyển một cách thật khôn khéo, lợi dụng địa hình để tránh đạn, khai hỏa chính xác và dành chiến thắng.
* Game gồm nhiều quy tắc: Quy tắc công trình, Quy tắc di chuyển, Quy tắc điều khiển bắn, Quy tắc chiến thắng, ...
* Chi tiết các bạn có thể đọc và tìm hiểu thêm trong 2 tài liệu mà BTC có đính kèm khi đăng ký tham gia cuộc thi để biết thêm chi tiết.

<p align="center">
<img src="./img/gameplay.gif" width="640" height="360"/>
</p>

## Game Mode

Game có 3 mode:
* Training Mode: Chế độ sử dụng cho việc training model AI 
* Autonomous Mode: Chế độ sử dụng cho việc test model AI
* Fight Mode: Chế độ PvP giữa các người chơi (được sử dụng khi thi đấu)

<p align="center">
<img src="./img/game_menu.png" width="640" height="360"/>
</p>

## Hướng dẫn chạy mã nguồn mở

Cấu trúc thư mục:
1. Thư mục Train: Chứa mã nguồn liên quan đến việc huấn luyện model AI
2. Thư mục Predict: Chứa mã nguồn liên quan đến việc chạy thử model AI
3. `game_server.cfg` : Config file chưa thông tin game
4. `test_server.py` : Sử dụng để test server kết nối thành công hay không
