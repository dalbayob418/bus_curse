SELECT t.T_ID, t.T_DATE, t.T_ENTRY_DATE, t.T_EXIT_DATE, t.T_TROLL_NUMBER,
       d.D_NAME as driver_name, r.R_NAME as route_name
FROM timesheet t
JOIN drivers d ON t.D_ID = d.D_ID
JOIN route r ON t.R_ID = r.R_ID
WHERE t.T_TROLL_NUMBER = %s