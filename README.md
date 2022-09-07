# Hello mọi người
## Hướng dẫn cài đặt môi trường cho conda
Bước 1: search từ "anaconda prompt" trong window. Sau khi mở lên thì nhìn sẽ giống cmd chỉ khác là có "(base)" trước địa chỉ, đó là environment đang sử dụng

![anaconda prompt](https://user-images.githubusercontent.com/75202089/179887248-1caaffa2-3c82-4099-8161-40885de23ab3.png)

Bước 2: Để tạo environment, ta gõ "conda create -n s2t_GCP_Final python=3.9" . Khi được hỏi Proceed thì hãy gõ "Y" và Enter. Conda sẽ tạo ra một môi trường mới có tên sau -n là "s2t_GCP_Final" và python có version 3.9. 

![image](https://user-images.githubusercontent.com/75202089/179888368-86e4e304-0ba2-4d41-b4bb-ade7a977a8bf.png)

Để chắc chắn là mình đã tạo môi trường thành công thì gõ lệnh "conda env list". Nếu có "s2t_GCP_Final" thì đã thành công

![image](https://user-images.githubusercontent.com/75202089/179888618-e579334a-41d7-4a56-96b2-e250a0a7f6b9.png)

Bước 3: Hãy kích hoạt môi trường bằng lệnh "conda activate s2t_GCP_Final" và thấy tên môi trường trước địa chỉ là thành công

![image](https://user-images.githubusercontent.com/75202089/179888917-8ae9918a-fecc-4667-902f-5a891a16cf0e.png)

Bước 4: Tải jupyter notebook, gõ lệnh "pip install jupyter"

Bước 5: Để môi trường truy cập vào địa chỉ project, gõ lệnh "cd path/to/project". Trong trường hợp ta để project ở ổ đĩa khác thì hãy gõ tên ổ đĩa và 2 chấm ví dụ "D:" sau đó gõ lệnh "cd path/to/project" 

![image](https://user-images.githubusercontent.com/75202089/179890054-0df11734-4246-4c18-a92a-276caf94f7a7.png)

Bước 6: Mở jupyter notebook, gõ lệnh "jupyter notebook"

Bước 7: Trong jupyter notebook, các bạn hãy mở merge_Final.ipynb là notebook hoàn thiện nhất hiện tại. Trong trường hợp các bạn muốn kiểm tra environment của jupyter notebook thì hãy tạo cell mới và gõ "!conda info", như hình dưới là bạn đã thành công

![image](https://user-images.githubusercontent.com/75202089/179890363-a55fcb01-64bf-4458-9d4d-85ac60e257f2.png)

Bước 8: Các bạn hãy run cell đầu tiên để tải thư viện rồi reset notebook bằng nhấn '00', nhớ là ấn vào chỗ đỏ như hình bên dưới. Sau đó chuyển cell đầu thành Markdown, bằng cách click vào chỗ tô màu đỏ bên dưới rồi nhấn "M". Sau đó run all để chạy thử

![image](https://user-images.githubusercontent.com/75202089/179891406-fe2fb898-541f-4c4b-a3e9-8ab722a1a982.png)
