CREATE OR REPLACE VIEW fraud_analysis_view AS
SELECT
   t.id AS transaction_id,
   t.date,
   t.amount,
   t.use_chip,
   t.merchant_state,
   t.is_fraud,


   u.id AS user_id,
   u.current_age,
   u.retirement_age,
   u.gender,
   u.credit_score,
   u.num_credit_cards,
   u.yearly_income,
   u.total_debt,


   c.id AS card_id,
   c.card_brand,
   c.card_type,
   c.has_chip,
   c.num_cards_issued,
   c.credit_limit,
   c.is_prepaid,


   HOUR(t.date) AS hour_of_day,
   DAYOFWEEK(t.date) AS day_of_week,
   MONTH(t.date) AS `month`,
   YEAR(t.date) AS `year`
FROM
   transactions t
JOIN
   users u ON t.client_id = u.id
JOIN
   cards c ON t.card_id = c.id;
