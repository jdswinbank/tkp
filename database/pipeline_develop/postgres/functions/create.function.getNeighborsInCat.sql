--DROP FUNCTION getNeighborsInCat;

create or replace FUNCTION getNeighborsInCat(icatname VARCHAR(50)
                                 ,itheta double precision
                                 ,ixtrsrcid INT
                                 ) RETURNS TABLE (catsrcid INT
                                                 ,distance_arcsec double precision
                                                 ) as $$
  DECLARE izoneheight double precision;

BEGIN
  
  /* TODO: 
   * retrieve zoneheight from table ->
   * meaning add a columns to the table
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  izoneheight := 1;

  RETURN query
    SELECT catsrcid
          ,3600 * degrees(2 * ASIN(SQRT((x1.x - c1.x) * (x1.x - c1.x)
                                       + (x1.y - c1.y) * (x1.y - c1.y)
                                       + (x1.z - c1.z) * (x1.z - c1.z)
                                       ) / 2) 
                         ) AS distance
      FROM extractedsources x1
          ,catalogedsources c1
          ,catalogs c0
     WHERE c1.cat_id = c0.catid
       AND c0.catname = icatname
       AND x1.xtrsrcid = ixtrsrcid
       AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(radians(itheta))
       AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                       AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
       AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                     AND x1.ra + alpha(itheta, x1.decl)
       AND c1.decl BETWEEN x1.decl - itheta
                       AND x1.decl + itheta
    ORDER BY distance
  ;

END
;
$$ language plpgsql;
