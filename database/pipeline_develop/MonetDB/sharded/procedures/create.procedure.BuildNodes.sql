--DROP PROCEDURE BuildNodes;

/**
 * This procedure builds the zones table according to
 * the input zoneheight and theta (both in degrees).
 * ATTENTION:
 * The zone column in the extractedsources table will NOT be modified!
 * It is best to run this before an observation,
 * i.e. at initialisation time,
 * and when you have an idea about the zoneheight.
 * TODO: Find out what a good zoneheight will be.
 */
CREATE PROCEDURE BuildNodes(inode_min INT, inode_max INT, max_incl BOOLEAN)
BEGIN

  DECLARE izone INT;

  SET izone = inode_min;
  IF max_incl THEN
    WHILE izone <= inode_max DO
      INSERT INTO node 
        (zone
        ,zoneheight
        )
      VALUES 
        (izone
        ,1.0
        )
      ;
      SET izone = izone + 1;
    END WHILE;
  ELSE
    WHILE izone < inode_max DO
      INSERT INTO node 
        (zone
        ,zoneheight
        )
      VALUES 
        (izone
        ,1.0
        )
      ;
      SET izone = izone + 1;
    END WHILE;
  END IF;

END;
