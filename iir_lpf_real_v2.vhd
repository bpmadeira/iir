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
	constant MUL_WIDTH : integer := COEFF_WIDTH + DATA_WIDTH; -- 32 + 16 = 48
	constant MUL_A_WIDTH : integer := COEFF_WIDTH + MUL_WIDTH; -- 32 + 48 = 80
	constant ASHIFT_WIDTH: integer := MUL_WIDTH - FRAC_WIDTH; -- 48 - 30 = 18
    
	----- SATURATION -----
	
	----- SIGNALS -----
	signal x_0, x_1, x_2: signed(DATA_WIDTH - 1 downto 0);
	signal y_2: signed(MUL_WIDTH - 1 downto 0);
	signal b0_m, b1_m, b2_m: signed(MUL_A_WIDTH - 1 downto 0);
	signal a1_m, a2_m: signed(MUL_A_WIDTH - 1 downto 0);
	signal y_1: signed(MUL_A_WIDTH - 1 downto 0) := (others => '0');
	signal a2_i, a1_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	signal b0_i, b1_i, b2_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	
	-- Add the attribute declaration here
    attribute dont_touch : string;
    -- Apply the attribute to the signals
    attribute dont_touch of x_0 : signal is "true";
    attribute dont_touch of y_2 : signal is "true";
    attribute dont_touch of x_1 : signal is "true";
    attribute dont_touch of y_1 : signal is "true";
    attribute dont_touch of x_2 : signal is "true";

    
    
begin
	
    process(data_clk_i) is
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
            	-- Update FIR values
            	x_2 <= signed(x_1); -- 32b
            	x_1 <= signed(x_0); -- 32b
            	x_0 <= signed(data_i_i); -- 32b
              y_2 <= signed(y_1(MUL_WIDTH-1 downto 0));
              b0_m <= resize(shift_right(signed(x_0*b0_i), FRAC_WIDTH), MUL_A_WIDTH); -- 32b * 32b (64b)
              b1_m <= resize(shift_right(signed(x_1*b1_i), FRAC_WIDTH), MUL_A_WIDTH); -- 32b * 32b (64b)
              b2_m <= resize(shift_right(signed(x_2*b2_i), FRAC_WIDTH), MUL_A_WIDTH); -- 32b * 32b (64b)
              a1_m <= shift_right(signed(y_1(MUL_WIDTH-1 downto 0)*a1_i), FRAC_WIDTH);
              a2_m <= shift_right(signed(y_2(MUL_WIDTH-1 downto 0)*a2_i), FRAC_WIDTH);
              y_1 <= signed(shift_right(b0_m + b1_m + b2_m - a1_m - a2_m,FRAC_WIDTH)); -- a1_m - a2_m, FRAC_WIDTH)); -- 64bit

            	
           	 end if;
           	 
        	end if;
    	end if;
	end process;

	data_i_o <= std_logic_vector(y_1(OUTPUT_WIDTH - 1 downto 0));
    data_en_o <= data_en_i;
    data_clk_o <= data_clk_i;
	data_rst_o <= data_rst_i;

end architecture bhv;
