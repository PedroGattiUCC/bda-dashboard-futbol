-- =============================================================================
-- Vista auxiliar para el dashboard (construida SOLO sobre el modelo estrella).
-- Cada partido de FACT_COMPETENCIA aparece dos veces: una desde el punto de
-- vista del equipo local y otra desde el visitante. Así los indicadores "por
-- equipo" (goles a favor, % de victorias, puntos, tarjetas, Elo) se calculan
-- con un simple GROUP BY equipo, sin repetir el CASE local/visitante.
-- =============================================================================

USE dw_competencia_futbol;

CREATE OR REPLACE VIEW V_PARTICIPACION AS
SELECT f.id_tiempo, f.id_division, f.id_pais,
       f.id_equipo_local     AS id_equipo,
       f.id_equipo_visitante AS id_rival,
       'Local'               AS condicion,
       f.goles_local         AS goles_favor,
       f.goles_visitante     AS goles_contra,
       f.puntos_local        AS puntos,
       f.victoria_local      AS victoria,
       f.empate              AS empate,
       f.victoria_visitante  AS derrota,
       f.elo_local           AS elo,
       f.amarillas_local     AS amarillas,
       f.rojas_local         AS rojas
FROM FACT_COMPETENCIA f
UNION ALL
SELECT f.id_tiempo, f.id_division, f.id_pais,
       f.id_equipo_visitante, f.id_equipo_local, 'Visitante',
       f.goles_visitante, f.goles_local, f.puntos_visitante,
       f.victoria_visitante, f.empate, f.victoria_local,
       f.elo_visitante, f.amarillas_visitante, f.rojas_visitante
FROM FACT_COMPETENCIA f;
