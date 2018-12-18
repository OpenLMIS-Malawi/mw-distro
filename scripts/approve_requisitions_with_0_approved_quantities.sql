-- Set all approved quantities to 0
WITH program_ids AS (
    SELECT p.id
    FROM referencedata.programs AS p
    WHERE p.code in ('tb')
), requisition_ids AS (
    SELECT r.id
	  FROM requisition.requisitions AS r
	  WHERE status = 'AUTHORIZED'
		  AND programid in (SELECT p.id FROM program_ids AS p)
		  AND processingperiodid in (
		      SELECT pp.id
		      FROM referencedata.processing_periods AS pp
		      WHERE pp.enddate < '2018-11-1'
		        AND pp.startdate > '2018-06-30')
)
UPDATE requisition.requisition_line_items AS rli
SET approvedquantity = 0
WHERE rli.requisitionid in (select r.id from requisition_ids AS r);

-- Add APPROVED status change
WITH program_ids AS (
    SELECT p.id
    FROM referencedata.programs AS p
    WHERE p.code in ('tb')
), requisition_ids AS (
    SELECT r.id
	  FROM requisition.requisitions AS r
	  WHERE status = 'AUTHORIZED'
		  AND programid in (SELECT p.id FROM program_ids AS p)
		  AND processingperiodid in (
		      SELECT pp.id
		      FROM referencedata.processing_periods AS pp
		      WHERE pp.enddate < '2018-11-1'
		        AND pp.startdate > '2018-06-30')
)
INSERT INTO requisition.status_changes (id, createddate, modifieddate, authorid, status, requisitionid)
SELECT uuid_generate_v4(), now(), now(), '35316636-6264-6331-2d34-3933322d3462', 'APPROVED', r.id
FROM requisition_ids AS r;

-- Change requisition status to APPROVED
WITH program_ids AS (
    SELECT p.id
    FROM referencedata.programs AS p
    WHERE p.code in ('tb')
), requisition_ids AS (
    SELECT r.id
	  FROM requisition.requisitions AS r
	  WHERE status = 'AUTHORIZED'
		  AND programid in (SELECT p.id FROM program_ids AS p)
		  AND processingperiodid in (
		      SELECT pp.id
		      FROM referencedata.processing_periods AS pp
		      WHERE pp.enddate < '2018-11-1'
		        AND pp.startdate > '2018-06-30')
)
UPDATE requisition.requisitions AS req
SET status = 'APPROVED'
WHERE req.id in (select r.id from requisition_ids AS r);