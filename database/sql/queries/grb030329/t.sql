SELECT ax2.xtrsrc_id 
      ,count(*) as datapoints 
      ,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy 
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax2 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2 
 WHERE ax2.xtrsrc_id = x1.xtrsrcid 
   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = im2.ds_id 
   AND im1.ds_id = 45
   /*AND im1.band = 14 
   AND im1.band = im2.band */
GROUP BY ax2.xtrsrc_id 
HAVING COUNT(*) > 8 
ORDER BY datapoints 
        ,ax2.xtrsrc_id
;

