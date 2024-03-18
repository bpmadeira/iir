library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity iir_lpf_real is
	generic (
    	DATA_WIDTH : natural := 32;
    	OUTPUT_WIDTH : natural := 64;
    	COEFF_WIDTH: natural := 32;
    	FRAC_WIDTH: natural := 30
	);
	port (
    	data_i_i   : in std_logic_vector(DATA_WIDTH-1 downto 0);
    	data_en_i  : in std_logic;
    	data_clk_i : in std_logic;
    	data_rst_i : in std_logic;
    	data_i_o   : out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	data_en_o  : out std_logic;
    	data_clk_o : out std_logic;
    	data_rst_o : out std_logic;
    	a1     	: in signed(COEFF_WIDTH-1 downto 0);
    	a1_en  	: in std_logic;
    	a1_clk 	: in std_logic;
    	a1_rst 	: in std_logic;
    	a2     	: in signed(COEFF_WIDTH-1 downto 0);
    	a2_en  	: in std_logic;
    	a2_clk 	: in std_logic;
    	a2_rst 	: in std_logic;
    	b0     	: in signed(COEFF_WIDTH-1 downto 0);
    	b0_en  	: in std_logic;
    	b0_clk 	: in std_logic;
    	b0_rst 	: in std_logic;
    	b1     	: in signed(COEFF_WIDTH-1 downto 0);
    	b1_en  	: in std_logic;
    	b1_clk 	: in std_logic;
    	b1_rst 	: in std_logic;
    	b2     	: in signed(COEFF_WIDTH-1 downto 0);
    	b2_en  	: in std_logic;
    	b2_clk 	: in std_logic;
    	b2_rst 	: in std_logic
	);
end entity iir_lpf_real;

architecture bhv of iir_lpf_real is

	----- CONSTANTS -----
	constant MUL_WIDTH : integer := COEFF_WIDTH + DATA_WIDTH;
	constant MUL_A_WIDTH : integer := COEFF_WIDTH + MUL_WIDTH;
	constant ASHIFT_WIDTH: integer := MUL_WIDTH - FRAC_WIDTH;
    
	----- SATURATION -----
	constant SAT_PLUS : signed(DATA_WIDTH - 1 downto 0):= (DATA_WIDTH-1 => '0', others => '1');
	constant SAT_MINUS : signed(DATA_WIDTH - 1 downto 0):= (DATA_WIDTH-1 => '1', others => '0');
    
	----- SIGNALS -----
	signal x_0, x_1, x_2: signed(DATA_WIDTH - 1 downto 0);
	signal y_1, y_2: signed(MUL_A_WIDTH - 1 downto 0);
	signal b0_m, b1_m, b2_m: signed(MUL_WIDTH - 1 downto 0);
	signal a1_m, a2_m: signed(MUL_A_WIDTH - 1 downto 0);
	signal iir_out: signed(MUL_A_WIDTH - 1 downto 0) := (others => '0');
	signal fir_output: signed(OUTPUT_WIDTH - 1 downto 0);
	signal a2_i, a1_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	signal b0_i, b1_i, b2_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
    
    
begin
    
	Coeff_Load: process(data_clk_i, data_rst_i)
	begin
	if rising_edge(data_clk_i) then
        	-- Coefficients Load
        	if a1_en = '1' then
            	a1_i <= a1;
        	end if;
        	if a2_en = '1' then
            	a2_i <= a2;
        	end if;
        	if b0_en = '1' then
            	b0_i <= b0;
        	end if;
        	if b1_en = '1' then
            	b1_i <= b1;
        	end if;
        	if b2_en = '1' then
            	b2_i <= b2;
        	end if;
        end if;
    end process Coeff_Load;

    X_Register: process(data_clk_i, data_rst_i)
    begin
    if rising_edge(data_clk_i) then
        if data_en_i = '1' then
            	-- Update FIR section
                x_0 <= signed(data_i_i); -- 32b
                x_1 <= x_0; -- 32b
            	x_2 <= x_1; -- 32b
        end if;
    end if;
    end process B_Register;

    Y_Register: process(data_clk_i, data_rst_i)
    begin
    if rising_edge(data_clk_i) then
        if data_en_i = '1' then
            	-- Update IIR section
                --y_1 <= shift_right(output,FRAC_WIDTH);
            	y_2 <= shift_right(y_1,FRAC_WIDTH); 
        end if;
    end if;
    end process B_Register;
            	
            	
    b0_m <= signed(x_0*b0_i); -- 32b * 32b (64b)
    b1_m <= signed(x_1*b1_i); -- 32b * 32b (64b)
    b2_m <= signed(x_2*b2_i); -- 32b * 32b (64b)
    a1_m <= signed(y_1(OUTPUT_WIDTH-1 downto 0)*a1_i);
    a2_m <= signed(y_2(OUTPUT_WIDTH-1 downto 0)*a2_i);
    y_1 <= b0_m + b1_m + b2_m - a1_m - a2_m;

    OutRegister : process (data_clk_i, data_rst_i)
    begin
        if data_rst_i = '1' then
            iir_out <= (others => '0');
        elsif data_clk_i'event AND data_clk_i = '1' then
            if data_en_i = '1' then
                iir_out <= shift_right(y_1,FRAC_WIDTH);   
            end if;
        end if;
    end process OutRegister;
            	
    data_i_o <= std_logic_vector(iir_out);
	data_en_o <= data_en_i;
	data_clk_o <= data_clk_i;
	data_rst_o <= data_rst_i;
end architecture bhv;
