-- =============================================================================
-- GUÍA DE TRABAJO PRÁCTICO #2: DATA WAREHOUSE CON METODOLOGÍA HEFESTO
-- Consigna 3: Paso 3 — Modelo Lógico del DW
-- Base de Datos: dw_competencia_futbol
-- Motor: MySQL 8.0+
-- =============================================================================

CREATE DATABASE IF NOT EXISTS dw_competencia_futbol
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE dw_competencia_futbol;

-- -----------------------------------------------------------------------------
-- Eliminación ordenada de tablas previas (respetando integridad referencial)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS FACT_COMPETENCIA;
DROP TABLE IF EXISTS DIM_TIEMPO;
DROP TABLE IF EXISTS DIM_EQUIPO;
DROP TABLE IF EXISTS DIM_DIVISION;
DROP TABLE IF EXISTS DIM_PAIS;

-- -----------------------------------------------------------------------------
-- 1. Dimensión: DIM_TIEMPO
-- Perspectiva de origen: Tiempo
-- Atributos: MatchDate, Temporada, Año, Mes, Trimestre, Día_Semana
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_TIEMPO (
    id_tiempo INT NOT NULL AUTO_INCREMENT,
    fecha DATE NOT NULL,                        -- MatchDate
    temporada VARCHAR(20) NOT NULL,             -- Ciclo competitivo (ej: '2021-2022' o '2021')
    anio SMALLINT NOT NULL,                     -- Año de MatchDate
    mes TINYINT NOT NULL,                       -- Número de mes (1-12)
    nombre_mes VARCHAR(20) NOT NULL,            -- Nombre del mes
    trimestre TINYINT NOT NULL,                 -- Trimestre (1-4)
    dia_semana VARCHAR(20) NOT NULL,            -- Día de la semana (Lunes, Martes, etc.)
    CONSTRAINT pk_dim_tiempo PRIMARY KEY (id_tiempo),
    CONSTRAINT uq_dim_tiempo_fecha UNIQUE (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. Dimensión: DIM_EQUIPO
-- Perspectivas de origen: Equipo (rol local) / Rival (rol visitante)
-- Atributos: HomeTeam / AwayTeam (Matches.csv), con TRIM y mapeo de variantes
-- de escritura detectadas en el Paso 2 (mapeos/mapeo_equipos.csv)
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_EQUIPO (
    id_equipo INT NOT NULL AUTO_INCREMENT,
    nombre_equipo VARCHAR(100) NOT NULL,        -- Nombre unificado/canónico del club
    CONSTRAINT pk_dim_equipo PRIMARY KEY (id_equipo),
    CONSTRAINT uq_dim_equipo_nombre UNIQUE (nombre_equipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. Dimensión: DIM_DIVISION
-- Perspectiva de origen: División / Liga
-- Atributos: Division (Matches.csv), Nombre_Liga
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_DIVISION (
    id_division INT NOT NULL AUTO_INCREMENT,
    codigo_division VARCHAR(10) NOT NULL,       -- Sigla original: 'E0', 'SP1', 'T1', etc.
    nombre_liga VARCHAR(100) NOT NULL,          -- Nombre formal: 'Premier League', 'La Liga', etc.
    CONSTRAINT pk_dim_division PRIMARY KEY (id_division),
    CONSTRAINT uq_dim_division_codigo UNIQUE (codigo_division)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. Dimensión: DIM_PAIS
-- Perspectiva de origen: País
-- Atributos: país derivado del código Division (Matches.csv)
-- -----------------------------------------------------------------------------
CREATE TABLE DIM_PAIS (
    id_pais INT NOT NULL AUTO_INCREMENT,
    codigo_pais CHAR(3) NOT NULL,               -- 'ENG', 'ESP', 'TUR', etc.
    nombre_pais VARCHAR(50) NOT NULL,           -- 'Inglaterra', 'España', 'Turquía', etc.
    CONSTRAINT pk_dim_pais PRIMARY KEY (id_pais),
    CONSTRAINT uq_dim_pais_codigo UNIQUE (codigo_pais)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. Tabla de Hechos: FACT_COMPETENCIA
-- Proceso Central: Competencia entre Equipos (partidos disputados)
-- Granularidad: Un registro por cada partido individual disputado.
-- Clave primaria compuesta por las claves foráneas de las dimensiones.
-- Hechos/Medidas base:
--   - Goles: FTHome, FTAway
--   - Resultado: FTResult ('H', 'D', 'A') y banderas derivadas
--   - Elo: HomeElo, AwayElo (NULL si el archivo no trae el dato)
--   - Disciplina: HomeYellow, AwayYellow, HomeRed, AwayRed (NULL si la liga no
--     informa tarjetas; no se imputa 0 para no sesgar los promedios)
--   - Puntos: derivados de FTResult (3 / 1 / 0)
-- -----------------------------------------------------------------------------
CREATE TABLE FACT_COMPETENCIA (
    -- Claves foráneas (conforman la Clave Primaria Compuesta según HEFESTO)
    id_tiempo INT NOT NULL,
    id_equipo_local INT NOT NULL,
    id_equipo_visitante INT NOT NULL,
    id_division INT NOT NULL,
    id_pais INT NOT NULL,

    -- Hechos y métricas directas del encuentro
    goles_local SMALLINT NOT NULL,              -- FTHome
    goles_visitante SMALLINT NOT NULL,          -- FTAway
    resultado CHAR(1) NOT NULL,                 -- FTResult ('H', 'D', 'A')
    elo_local DECIMAL(6,2) NULL,                -- HomeElo
    elo_visitante DECIMAL(6,2) NULL,            -- AwayElo
    amarillas_local SMALLINT NULL,              -- HomeYellow
    amarillas_visitante SMALLINT NULL,          -- AwayYellow
    rojas_local SMALLINT NULL,                  -- HomeRed
    rojas_visitante SMALLINT NULL,              -- AwayRed

    -- Hechos derivados de FTResult
    puntos_local TINYINT NOT NULL,              -- 3 si 'H', 1 si 'D', 0 si 'A'
    puntos_visitante TINYINT NOT NULL,          -- 3 si 'A', 1 si 'D', 0 si 'H'
    victoria_local TINYINT NOT NULL,            -- 1 si resultado = 'H'
    empate TINYINT NOT NULL,                    -- 1 si resultado = 'D'
    victoria_visitante TINYINT NOT NULL,        -- 1 si resultado = 'A'

    -- Clave primaria compuesta
    CONSTRAINT pk_fact_competencia PRIMARY KEY (
        id_tiempo,
        id_equipo_local,
        id_equipo_visitante,
        id_division,
        id_pais
    ),

    CONSTRAINT ck_fact_competencia_resultado CHECK (resultado IN ('H', 'D', 'A')),

    -- Claves foráneas hacia las dimensiones
    CONSTRAINT fk_competencia_tiempo
        FOREIGN KEY (id_tiempo)
        REFERENCES DIM_TIEMPO (id_tiempo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_competencia_equipo_local
        FOREIGN KEY (id_equipo_local)
        REFERENCES DIM_EQUIPO (id_equipo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_competencia_equipo_visitante
        FOREIGN KEY (id_equipo_visitante)
        REFERENCES DIM_EQUIPO (id_equipo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_competencia_division
        FOREIGN KEY (id_division)
        REFERENCES DIM_DIVISION (id_division)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_competencia_pais
        FOREIGN KEY (id_pais)
        REFERENCES DIM_PAIS (id_pais)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Índices para optimización de consultas analíticas sobre los roles de equipo
-- -----------------------------------------------------------------------------
CREATE INDEX idx_fact_competencia_local ON FACT_COMPETENCIA(id_equipo_local);
CREATE INDEX idx_fact_competencia_visitante ON FACT_COMPETENCIA(id_equipo_visitante);
CREATE INDEX idx_fact_competencia_division ON FACT_COMPETENCIA(id_division);
CREATE INDEX idx_fact_competencia_pais ON FACT_COMPETENCIA(id_pais);
CREATE INDEX idx_fact_competencia_tiempo ON FACT_COMPETENCIA(id_tiempo);
