DELIMITER $$
DROP PROCEDURE IF EXISTS AUTO_ORDER_CONFIRM
CREATE PROCEDURE AUTO_ORDER_CONFIRM( OUT RESULT INT)
/*
AUTO_ORDER_CONFIRM 프로시저
	order_item_info 테이블에 배송완료상태 주문을 이력 종료시키고, 구매확정상태 주문을 새로 생성한다.

Authors:
    eymin1259@gmail.com 이용민

History:
    2020-10-05 (이용민) : 초기 생성
*/
BEGIN

    /* 오토커밋 ON, 트랜잭션 설정 */
    SET AUTOCOMMIT = 1;
    START TRANSACTION;

	/* 커서 종료 구분 변수 */
	DECLARE _done INT DEFAULT FALSE;
	/* 처리된 건수 */
	DECLARE _row_count INT DEFAULT 0;
    /*구매확정 프로시저 실행 시간*/
    DECLARE auto_comfirm_time DATETIME DEFAULT now();

    /* order_item_info 테이블(oii)의 컬럼값을 담을 변수 */
    DECLARE _oii_id INT;
    DECLARE _oii_order_detail_id VARCHAR(45);
    DECLARE _oii_order_id INT;
    DECLARE _oii_order_status_id INT;
    DECLARE _oii_product_id INT;
    DECLARE _oii_price DECIMAL(18,0);
    DECLARE _oii_option_color VARCHAR(45);
    DECLARE _oii_option_size VARCHAR(45);
    DECLARE _oii_option_additional_price DECIMAL(18,0);
    DECLARE _oii_units INT;
    DECLARE _oii_discount_price INT;
    DECLARE _oii_shipping_start_date DATETIME;
    DECLARE _oii_shipping_complete_date DATETIME;
    DECLARE _oii_shipping_company VARCHAR(45);
    DECLARE _oii_shipping_number INT:
    DECLARE _oii_is_confirm_order TINYINT;
    DECLARE _oii_refund_request_date DATETIME;
    DECLARE _oii_refund_complete_date DATETIME;
    DECLARE _oii_refund_reason_id INT;
    DECLARE _oii_refund_amount INT;
    DECLARE _oii_refund_shipping_fee INT;
    DECLARE _oii_detail_reason VARCHAR(1024);
    DECLARE _oii_bank VARCHAR(45);
    DECLARE _oii_account_holder VARCHAR(45);
    DECLARE _oii_account_number VARCHAR(45);
    DECLARE _oii_cancel_reason_id INT;
    DECLARE _oii_complete_cancellation_date DATETIME;
    DECLARE _oii_start_date DATETIME;
    DECLARE _oii_end_date DATETIME;
    DECLARE _oii_modifier_id INT;
    DECLARE _oii_is_deleted TINYINT;

	/* order_item_info 테이블에서 배송완료일(order_status_id = 4)이 3일이상 지난 row들을 읽어오는 커서를 생성. */
	DECLARE CURSOR_ORDER_ITEM_INFO CURSOR FOR 
    SELECT * 
    FROM order_item_info 
    WHERE order_status_id = 4 
    AND shipping_complete_date <= DATE_SUB(now(), interval 3 day);

	/* 커서 종료조건 : 더이상 없다면 종료 */
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET _done = TRUE;

	OPEN CURSOR_ORDER_ITEM_INFO;
	REPEAT
        /* 배송완료상태의 주문 data를 fetch*/
        FETCH CURSOR_ORDER_ITEM_INFO INTO _oii_id, _oii_order_detail_id, _oii_order_id, _oii_order_status_id, _oii_product_id, _oii_price, _oii_option_color, _oii_option_size, _oii_option_additional_price, _oii_units, _oii_discount_price, _oii_shipping_start_date, _oii_shipping_complete_date, _oii_shipping_company, _oii_shipping_number, _oii_is_confirm_order, _oii_refund_request_date, _oii_refund_complete_date, _oii_refund_reason_id, _oii_refund_amount, _oii_refund_shipping_fee, _oii_detail_reason, _oii_bank, _oii_account_holder, _oii_account_number, _oii_cancel_reason_id, _oii_complete_cancellation_date, _oii_start_date, _oii_end_date, _oii_modifier_id, _oii_is_deleted;
        IF NOT _done THEN

            /* 배송완료상태 종료*/
            UPDATE order_item_info 
            SET end_date = auto_comfirm_time, is_deleted = 1 
            WHERE id = _oii_id;
            
            /* fetch한 배송완료상태 주문 정보를 가지고 구매확정상태 주문 생성*/
            INSERT INTO order_item_info 
            VALUES( DEFAULT, _oii_order_detail_id, _oii_order_id, 5, _oii_product_id, _oii_price, _oii_option_color, _oii_option_size, _oii_option_additional_price, _oii_units, _oii_discount_price, _oii_shipping_start_date, _oii_shipping_complete_date, _oii_shipping_company, _oii_shipping_number, 1, _oii_refund_request_date, _oii_refund_complete_date, _oii_refund_reason_id, _oii_refund_amount, _oii_refund_shipping_fee, _oii_detail_reason, _oii_bank, _oii_account_holder, _oii_account_number, _oii_cancel_reason_id, _oii_complete_cancellation_date, auto_comfirm_time, '9999-12-31 23:59:59', _oii_modifier_id, 0 ); 

            SET _row_count = _row_count + 1;
			SET _done = FALSE;

		END IF;
	UNTIL _done END REPEAT;

	/* 커서를 닫기 */
	CLOSE CURSOR_ORDER_ITEM_INFO;
	SET RESULT = _row_count;
    	 
END$$
DELIMITER ;