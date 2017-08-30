package com.cras.update;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;

public class UpdateCRAS {
	
	public static final String SEPARATOR = ",";
	
	static Connection bbddConnection = null;
	static Statement st = null;
	
	static String url = "jdbc:postgresql://localhost:22100/CRAs";
	static String user = "";
	static String pass = "";
	
	public static boolean rowExists(String year, String id_mun, String mun, String entity) {
		
		boolean result = false;
		
		ResultSet rs = null;
		
		try {
		
			bbddConnection = DriverManager.getConnection(url, user, pass);
			st = bbddConnection.createStatement();
			rs = st.executeQuery("SELECT id, id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total," + 
									  	   "cero_años, un_año, dos_años, tres_años, cuatro_años, cinco_años, primero,"+
									  	   "segundo, tercero, cuarto, quinto, sexto, primero_eso, segundo_eso, año "+
									  	   "FROM educ_cra_evol WHERE año = '" + year + "' and id_mun = '" + id_mun + "';");
			
			result = rs.next();
		
			rs.close();
			st.close();
			bbddConnection.close();
		
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
		
		/*if (rs != null) {
			result = true;
		}*/
		
		return result;
	}
	
	public static void update (String year, String id_mun, String mun, String value, String type, String group, String total) {

		try {
		
			bbddConnection = DriverManager.getConnection(url, user, pass);
			PreparedStatement ps = null;
			int amountTotal = Integer.parseInt(total) + Integer.parseInt(value);
			
			if (type.equalsIgnoreCase("0 años")) {
				 ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET cero_años = cero_años + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("1 año")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET un_año = un_año + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("2 años")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET dos_años = dos_años + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("3 años")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET tres_años = tres_años + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("4 años")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET cuatro_años = cuatro_años + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("5 años")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET cinco_años = cinco_años + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("primero") && group.equalsIgnoreCase("E. Primaria")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET primero = primero + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("segundo") && group.equalsIgnoreCase("E. Primaria")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET segundo = segundo + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("tercero")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET tercero = tercero + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("cuarto")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET cuarto = cuarto + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("quinto")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET quinto = quinto + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("sexto")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET sexto = sexto + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("primero") && group.equalsIgnoreCase("E.S.O.")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET primero_eso = primero_eso + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			} else if (type.equalsIgnoreCase("segundo") && group.equalsIgnoreCase("E.S.O.")) {
				ps = bbddConnection.prepareStatement("UPDATE educ_cra_evol SET segundo_eso = segundo_eso + ?, total = ? WHERE año = ? and id_mun = ? and municipio_sede_del_cra = ?");
			}
			if (ps != null) {
				ps.setLong(1, Long.parseLong(value));
				ps.setLong(2, new Long(amountTotal));
				ps.setString(3, year);
				ps.setLong(4, Long.parseLong(id_mun));
				ps.setString(5, mun);
				ps.executeUpdate();
				System.out.println("UPDATED ---> " + year + " | " + id_mun + " | " + mun + " | " + value + " | " + type + " | " + total);
				ps.close();
			}
			
			bbddConnection.close();
		
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}
	
	public static void insert (String year, String id_mun, String mun, String craName, String craId, String value, String type, String group) {
		
		try {
			
			bbddConnection = DriverManager.getConnection(url, user, pass);
			st = bbddConnection.createStatement();
			String insertSQL = "";
			String valuesSQL = "";
			
			if (type.equalsIgnoreCase("0 años")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, cero_años, año)";
			} else if (type.equalsIgnoreCase("1 año")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, un_año, año)";
			} else if (type.equalsIgnoreCase("2 años")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, dos_años, año)";
			} else if (type.equalsIgnoreCase("3 años")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, tres_años, año)";
			} else if (type.equalsIgnoreCase("4 años")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, cuatro_años, año)";
			} else if (type.equalsIgnoreCase("5 años")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, cinco_años, año)";
			} else if (type.equalsIgnoreCase("primero") && group.equalsIgnoreCase("E. Primaria")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, primero, año)";
			} else if (type.equalsIgnoreCase("segundo") && group.equalsIgnoreCase("E. Primaria")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, segundo, año)";
			} else if (type.equalsIgnoreCase("tercero")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, tercero, año)";
			} else if (type.equalsIgnoreCase("cuarto")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, cuarto, año)";
			} else if (type.equalsIgnoreCase("quinto")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, quinto, año)";
			} else if (type.equalsIgnoreCase("sexto")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, sexto, año)";
			} else if (type.equalsIgnoreCase("primero") && group.equalsIgnoreCase("E.S.O.")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, primero_eso, año)";
			} else if (type.equalsIgnoreCase("segundo") && group.equalsIgnoreCase("E.S.O.")) {
				insertSQL = "INSERT INTO educ_cra_evol(id_mun, municipio_sede_del_cra, id_cra, nombre_del_cra, total, segundo_eso, año)";
			}
			valuesSQL = " VALUES ("+id_mun+", '"+mun+"', "+craId+", '"+craName+"', "+value+", "+value+", '"+year+"')";
			insertSQL = insertSQL.concat(valuesSQL);
			st.executeUpdate(insertSQL);
			System.out.println("INSERTED ---> " + year + " | " + id_mun + " | " + mun + " | " + value + " | " + type + " | " + craId + " | " + craName);
			st.close();
			bbddConnection.close();
			
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}
	
	public static int getCRAId (String craName) {
		
		int result = 0;
		
		ResultSet rs = null;
		
		try {
		
			bbddConnection = DriverManager.getConnection(url, user, pass);
			st = bbddConnection.createStatement();
			rs = st.executeQuery("SELECT id_cra FROM educ_cra where cra = '"+craName+"'");
			
			if (rs.next()) {
				result = rs.getInt(1);
			}
		
			rs.close();
			st.close();
			bbddConnection.close();
		
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
		
		return result;
	}
	
	public static int getTotalValuesByCRA (String year, String id_mun, String mun) {
		int result = 0;
		
		ResultSet rs = null;
		String querySQL = "";
		
		try {
		
			bbddConnection = DriverManager.getConnection(url, user, pass);
			st = bbddConnection.createStatement();
			querySQL = "SELECT total FROM educ_cra_evol WHERE año = '"+year+"' AND id_mun = '"+id_mun+"' and municipio_sede_del_cra = '"+mun+"'";
			rs = st.executeQuery(querySQL);
			
			
			if (rs.next()) {
				result = rs.getInt(1);
			}
			rs.close();
			st.close();
			bbddConnection.close();
		
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
		
		return result;
	}

	public static void main(String[] args) throws IOException {
		
		BufferedReader br = null;
		
		try {
			
			String yearArg = args[0];
			
			br = new BufferedReader(new InputStreamReader(new FileInputStream("bi_iaest_source.csv"), "utf-8"));
			String line = br.readLine();
			System.out.println("Reading file...");

			while (null!=line) {
				String [] fields = line.split(SEPARATOR);
				String year = fields[0];
				String craName = fields[1];
				String entity = fields[2];
				String id_mun = fields[3];
				String mun = fields[4];
				String value = fields[5];
				String type = fields[7];
				String group = fields[9];
				
				if (year.equalsIgnoreCase(yearArg)) {
					if (rowExists(year, id_mun, mun, entity)) {
						String total = String.valueOf(getTotalValuesByCRA(year, id_mun, mun));
						update(year, id_mun, mun, value, type, group, total);
					} else {
						String craId = String.valueOf(getCRAId(craName));
						insert(year, id_mun, mun, craName, craId, value, type, group);
					}
				}

				line = br.readLine();
			}
		} catch (Exception e) {
			System.out.println(e);
		} finally {
			if (null!=br) {
				br.close();
			}
		}	
	}
}
