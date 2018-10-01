CREATE FUNCTION packs_to_ship(line uuid, orderable uuid)
RETURNS BIGINT AS $$
DECLARE
  pack_rounding_threshold BIGINT;
	round_to_zero BOOLEAN;
	net_content BIGINT;
	quantity INTEGER;
	packs_to_order BIGINT;
	remainder_quantity BIGINT;
BEGIN
  SELECT approvedquantity INTO quantity FROM requisition.requisition_line_items WHERE id = $1;
  SELECT packRoundingThreshold, roundToZero, netContent INTO pack_rounding_threshold, round_to_zero, net_content FROM referencedata.orderables WHERE id = $2;

	IF quantity <= 0 OR net_content = 0 THEN
	  RETURN 0;
	END IF;

	packs_to_order := quantity / net_content;
	remainder_quantity := quantity % net_content;

	IF remainder_quantity > 0 AND remainder_quantity > pack_rounding_threshold THEN
	  packs_to_order := packs_to_order + 1;
	END IF;

	IF packs_to_order = 0 AND round_to_zero IS FALSE THEN
		packs_to_order := 1;
	END IF;

	RETURN packs_to_order;
END;
$$ LANGUAGE plpgsql;

UPDATE referencedata.orderables AS o SET netcontent = 10 WHERE o.code = 'BB059400';
UPDATE referencedata.orderables AS o SET netcontent = 1000 WHERE o.code = 'AA000901';

UPDATE
	requisition.requisition_line_items rli
SET
	packstoship = packs_to_ship(rli.id, rli.orderableId)
FROM
	requisition.requisitions r,
	referencedata.processing_periods p,
	referencedata.orderables o
WHERE
  r.id = rli.requisitionId
	AND p.id = r.processingPeriodId
	AND rli.orderableid = o.id
	AND o.code IN ('BB059400', 'AA000901');

UPDATE
  fulfillment.order_line_items oli
SET
  orderedquantity = rli.packstoship
FROM
  fulfillment.orders o,
	requisition.requisitions r,
	requisition.requisition_line_items rli,
	referencedata.processing_periods p,
	referencedata.orderables orderable
WHERE
  oli.orderId = o.id
	AND o.externalId = r.id
	AND r.id = rli.requisitionId
	AND oli.orderableId = rli.orderableId
	AND p.id = r.processingPeriodId
	AND rli.orderableid = orderable.id
	AND orderable.code IN ('BB059400', 'AA000901');

DROP FUNCTION packs_to_ship(line uuid, orderable uuid);