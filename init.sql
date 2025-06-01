-- init.sql
-- Chú ý: Các lệnh CREATE DATABASE/USER không cần thiết nếu dùng POSTGRES_DB/USER/PASSWORD
-- NHƯNG CHÚNG TA ĐỂ Ở ĐÂY ĐỂ ĐẢM BẢO TUYỆT ĐỐI NGƯỜI DÙNG ĐƯỢC TẠO CHÍNH XÁC.

-- Tạo người dùng nếu chưa tồn tại
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'tuan_phong') THEN
      CREATE ROLE tuan_phong WITH LOGIN PASSWORD 'Phong2525132546879!';
   END IF;
END
$do$;

-- Gán quyền cho người dùng tuan_phong trên database be_assign (được tạo tự động bởi POSTGRES_DB)
-- Nếu database 'be_assign' đã được tạo bởi biến môi trường POSTGRES_DB,
-- lệnh này sẽ gán quyền cho user 'tuan_phong' trên database đó.
GRANT ALL PRIVILEGES ON DATABASE be_assign TO tuan_phong;

-- Các lệnh CREATE TABLE của bạn sẽ nằm dưới đây
-- Ví dụ:
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    subject VARCHAR(255) NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender
        FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS message_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    recipient_id UUID NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT fk_message
        FOREIGN KEY (message_id)
        REFERENCES messages(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_recipient
        FOREIGN KEY (recipient_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_message_recipient UNIQUE (message_id, recipient_id)
);