/*
EVENT_AUTO_ORDER_CONFIRM 이벤트
	 매일 1회 AUTO_ORDER_CONFIRM 프로시저를 실행하는 이벤트 생성하고 스케쥴을 걸어 프로시저 자동 실행

Authors:
    eymin1259@gmail.com 이용민

History:
    2020-10-05 (이용민) : 초기 생성
*/

CREATE EVENT IF NOT EXISTS EVENT_AUTO_ORDER_CONFIRM
    ON SCHEDULE
    EVERY 1 DAY
    DO CALL AUTO_ORDER_CONFIRM()
END