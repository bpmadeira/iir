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
    	b2_rst 	: in std_logic;
    	test1  	: out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	test1_en   : out std_logic;
    	test1_clk   : out std_logic;
    	test1_rst  : out std_logic;
    	test2  	: out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	test2_en   : out std_logic;
    	test2_clk  : out std_logic;
    	test2_rst  : out std_logic
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
	signal iir_input: signed(MUL_A_WIDTH - 1 downto 0) := (others => '0');
	signal fir_output: signed(OUTPUT_WIDTH - 1 downto 0);
	signal output: signed(MUL_A_WIDTH - 1 downto 0);
	signal a2_i, a1_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	signal b0_i, b1_i, b2_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
    
    
begin
	data_i_o <= std_logic_vector(output(MUL_A_WIDTH - 1 downto 32));
	test1 <= std_logic_vector(output(63 downto 0));
	test2 <= std_logic_vector(fir_output);
	data_en_o <= data_en_i;
	data_clk_o <= data_clk_i;
	data_rst_o <= data_rst_i;
	test1_en <= data_en_i;
	test1_clk <= data_clk_i;
	test1_rst <= data_rst_i;
	test2_en <= data_en_i;
	test2_clk <= data_clk_i;
	test2_rst <= data_rst_i;
    
	process(data_clk_i) is
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
       	 
        	-- Direct Form I
        	if data_en_i = '1' then
            	-- Update FIR values
            	x_2 <= x_1; -- 32b
            	x_1 <= x_0; -- 32b
            	x_0 <= signed(data_i_i); -- 32b
                
            	-- FIR
            	b0_m <= signed(x_0*b0_i); -- 32b * 32b (64b)
            	b1_m <= signed(x_1*b1_i); -- 32b * 32b (64b)
            	b2_m <= signed(x_2*b2_i); -- 32b * 32b (64b)
            	a1_m <= signed(y_1(OUTPUT_WIDTH-1 downto 0)*a1_i);
            	a2_m <= signed(y_2(OUTPUT_WIDTH-1 downto 0)*a2_i);
            	fir_output <= b0_m + b1_m + b2_m;
            	iir_input <= resize(fir_output,MUL_A_WIDTH);
            	
            	output <= iir_input + a1_m + a2_m;     
            	
            	y_1 <= shift_right(output,FRAC_WIDTH);
            	y_2 <= y_1;      	
           	 
           	 
        	end if;
    	end if;
	end process;
end architecture bhv;

