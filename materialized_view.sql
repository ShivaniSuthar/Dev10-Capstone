DROP TABLE IF EXISTS fraud_analysis_table;


CREATE TABLE fraud_analysis_table AS
SELECT * FROM fraud_analysis_view;


ALTER TABLE fraud_analysis_table ADD INDEX idx_transaction_date (date);
ALTER TABLE fraud_analysis_table ADD INDEX idx_user_id (user_id);
ALTER TABLE fraud_analysis_table ADD INDEX idx_card_id (card_id);
ALTER TABLE fraud_analysis_table ADD INDEX idx_merchant_state (merchant_state);
ALTER TABLE fraud_analysis_table ADD INDEX idx_is_fraud (is_fraud);

