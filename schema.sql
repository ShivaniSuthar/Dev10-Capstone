DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
   id INT NOT NULL,
   current_age INT,
   retirement_age INT,
   gender VARCHAR(10),
   yearly_income FLOAT,
   total_debt FLOAT,
   credit_score INT,
   num_credit_cards INT,
   PRIMARY KEY (id),
   INDEX idx_user_credit_score (credit_score),
   INDEX idx_user_income (yearly_income)
);


CREATE TABLE cards (
   id INT NOT NULL,
   client_id INT NOT NULL,
   card_brand VARCHAR(50),
   card_type VARCHAR(20),
   has_chip TINYINT(1),
   num_cards_issued INT,
   credit_limit FLOAT,
   is_prepaid TINYINT(1),
   expiry_year INT,
   expiry_month INT,
   acct_open_year INT,
   acct_open_month INT,
   PRIMARY KEY (id),
   INDEX idx_card_client (client_id),
   INDEX idx_card_type (card_type),
   INDEX idx_card_expiry (expiry_year, expiry_month),
   FOREIGN KEY (client_id) REFERENCES users (id)
);


CREATE TABLE transactions (
   id BIGINT NOT NULL,
   `date` DATETIME,
   client_id INT,
   card_id INT,
   amount FLOAT,
   use_chip VARCHAR(20),
   merchant_state VARCHAR(2),
   is_fraud TINYINT(1) DEFAULT 0,
   PRIMARY KEY (id),
   INDEX idx_transaction_date (`date`),
   INDEX idx_transaction_card (card_id),
   INDEX idx_transaction_client (client_id),
   INDEX idx_transaction_amount (amount),
   INDEX idx_transaction_state (merchant_state),
   INDEX idx_transaction_fraud (is_fraud),
   INDEX idx_transaction_date_fraud (`date`, is_fraud),
   FOREIGN KEY (card_id) REFERENCES cards (id),
   FOREIGN KEY (client_id) REFERENCES users (id)
);
