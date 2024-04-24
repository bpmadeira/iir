library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity iir_lpf_real is
	generic (
    	DATA_WIDTH : natural := 20;
    	OUTPUT_WIDTH : natural := 64;
    	COEFF_WIDTH: natural := 40;
    	READ_SHIFT: natural := 0;
    	INTERNAL_SHIFT: natural := 6;
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
	constant MUL_WIDTH : integer := COEFF_WIDTH + DATA_WIDTH; -- 32 + 16 = 48
	constant MUL_A_WIDTH : integer := COEFF_WIDTH + MUL_WIDTH; -- 32 + 48 = 80
    
	----- SATURATION -----
	
	----- SIGNALS -----
	signal x_1, x_2: signed(MUL_WIDTH - 1 downto 0);
	signal y_2: signed(MUL_A_WIDTH - 1 downto 0);
	signal b0_m, b1_m, b2_m: signed(MUL_WIDTH - 1 downto 0);
	signal sum1,sum2,out_reg: signed(OUTPUT_WIDTH - 1 downto 0);
	signal sub1,sub2,x_0: signed(MUL_A_WIDTH - 1 downto 0);
	signal a1_m, a2_m: signed(MUL_A_WIDTH - 1 downto 0);
	signal y_1: signed(MUL_A_WIDTH - 1 downto 0) := (others => '0');
	signal a2_i, a1_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	signal b0_i, b1_i, b2_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	
	attribute dont_touch : string;

    -- Apply the dont_touch attribute to specific signals
    attribute dont_touch of y_1 : signal is "true";
    attribute dont_touch of out_reg : signal is "true";
  
begin
	data_i_o <= std_logic_vector(out_reg);
	data_en_o <= data_en_i;
	data_clk_o <= data_clk_i;
	data_rst_o <= data_rst_i;
	
	process(data_clk_i,data_rst_i) is
	begin
	if rising_edge(data_clk_i) then
	   if data_rst_i = '1' then
		-- Reset internal states
		x_0 <= (others => '0');
		x_1 <= (others => '0');
		x_2 <= (others => '0');
		y_1 <= (others => '0');
		y_2 <= (others => '0');
		b0_m <= (others => '0');
		b1_m <= (others => '0');
		b2_m <= (others => '0');
		a1_m <= (others => '0');
		a2_m <= (others => '0');
		out_reg <= (others => '0');
		a1_i <= (others => '0');
		a2_i <= (others => '0');
		b0_i <= (others => '0');
		b1_i <= (others => '0');
		b2_i <= (others => '0');
	    else
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
			b0_m <= signed(data_i_i)*b0_i;
			b1_m <= signed(data_i_i)*b1_i;
			b2_m <= signed(data_i_i)*b2_i; 
			x_0 <= resize(b0_m + x_1 , MUL_A_WIDTH);
			x_1 <= b1_m + x_2;
			x_2 <= b2_m;
			y_2 <= shift_left(x_0, INTERNAL_SHIFT) - shift_right(y_1,FRAC_WIDTH)(MUL_WIDTH+READ_SHIFT-1 downto READ_SHIFT)*a2_i;
			y_1 <= y_2 - shift_right(y_1,FRAC_WIDTH)(MUL_WIDTH+READ_SHIFT-1 downto READ_SHIFT)*a1_i;
			out_reg <= shift_right(y_1,FRAC_WIDTH)(OUTPUT_WIDTH-1 downto 0);
		end if; 
	    end if;
	end if;
	end process;


end architecture bhv;
