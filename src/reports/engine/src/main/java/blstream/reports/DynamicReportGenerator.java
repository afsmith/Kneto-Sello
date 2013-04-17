package blstream.reports;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;

import net.sf.jasperreports.engine.JRDataSource;
import net.sf.jasperreports.engine.JREmptyDataSource;
import net.sf.jasperreports.engine.JRException;
import net.sf.jasperreports.engine.JRExporterParameter;
import net.sf.jasperreports.engine.JRSubreport;
import net.sf.jasperreports.engine.JasperCompileManager;
import net.sf.jasperreports.engine.JasperExportManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;
import net.sf.jasperreports.engine.data.JRCsvDataSource;
import net.sf.jasperreports.engine.design.JRDesignExpression;
import net.sf.jasperreports.engine.design.JRDesignParameter;
import net.sf.jasperreports.engine.design.JRDesignSubreport;
import net.sf.jasperreports.engine.design.JasperDesign;
import net.sf.jasperreports.engine.export.JRCsvExporter;
import net.sf.jasperreports.engine.export.JRHtmlExporter;
import net.sf.jasperreports.engine.export.JRHtmlExporterParameter;
import net.sf.jasperreports.engine.util.JRElementsVisitor;
import net.sf.jasperreports.engine.util.JRProperties;
import net.sf.jasperreports.engine.util.JRVisitorSupport;
import net.sf.jasperreports.engine.xml.JRXmlLoader;
import net.sf.jasperreports.engine.xml.JRXmlWriter;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Appender;
import org.apache.log4j.ConsoleAppender;
import org.apache.log4j.FileAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;
import org.apache.log4j.PropertyConfigurator;

import ar.com.fdvs.dj.core.DynamicJasperHelper;
import ar.com.fdvs.dj.core.layout.ClassicLayoutManager;
import ar.com.fdvs.dj.domain.DynamicReport;
import ar.com.fdvs.dj.domain.Style;
import ar.com.fdvs.dj.domain.builders.FastReportBuilder;
import ar.com.fdvs.dj.domain.constants.Font;

public class DynamicReportGenerator {

	private static Logger log = Logger.getLogger(DynamicReportGenerator.class);

	private static final String COLUMN_NAME_PREFIX = "COLUMN_";

	public static final String JASPER_SUFFIX = ".jasper";

	public static final String JRXML_SUFFIX = ".jrxml";

	public static final String TMP_PREFIX = "tmp";

	public static final String ENCODING = "UTF-8";

	private static final char DELIMITER = ',';

	public static final String QUOTE = "\"";

	private static final String DATA_URL = "DATA_URL";

	private static final String USE_WEBSERVICE = "use_webservice";

	private static final List<File> tmpFiles = new ArrayList<File>();

	private static final String LOG4J_CONFIG_FILE = "log4j.properties";

	private static Properties props = new Properties();

	private static final String DB_HOST = "DB_HOST";
	private static final String DB_PORT = "DB_PORT";
	private static final String DB_DATABASE = "DB_DATABASE";
	private static final String DB_USER = "DB_USER";
	private static final String DB_PASS = "DB_PASS";

	private static void deleteTempFiles() {
		for (File tmpFile : tmpFiles) {
			FileUtils.deleteQuietly(tmpFile);
		}
	}

	private static String encodeWhiteSpaces(String URL) {
		return URL.replaceAll(" ", "%20");
	}

	private static void configureLog4j() {

		File file = new File(DynamicReportGenerator.LOG4J_CONFIG_FILE);
		if (file.exists()) {
			PropertyConfigurator.configure(DynamicReportGenerator.LOG4J_CONFIG_FILE);
		} else {
			Logger logger = Logger.getLogger("blstream.reports");
			Appender appender = null;
			try {
				appender = new FileAppender(new PatternLayout("%d %-5p [%c] %m%n"), "reports.log");
			} catch (IOException e) {
				appender = new ConsoleAppender(new PatternLayout("%d %-5p [%c] %m%n"));
			}
			logger.addAppender(appender);
			logger.setLevel(Level.DEBUG);
		}
		DynamicReportGenerator.log = Logger.getLogger("blstream.reports");
	}

	@SuppressWarnings("rawtypes")
	private static File generateDynamicReports(String URL, String ownerId) throws ReportGenerationException {
		try {
			URL = encodeWhiteSpaces(URL);
			File jrxml = getTemporaryJRXML();
			String columns[] = getColumnNames(URL, ownerId);
			FastReportBuilder drb = new FastReportBuilder();
			for (int index = 0; index < columns.length; index++) {
				Style style = new Style();
				style.setFont(new Font(Font.MEDIUM, Font._FONT_TIMES_NEW_ROMAN, "Helvetica", "Cp1252", true));
				Style headerStyle = new Style();
				headerStyle.setFont(new Font(Font.MEDIUM, Font._FONT_TIMES_NEW_ROMAN, "Helvetica", "Cp1252", true));
				headerStyle.getFont().setBold(true);
				drb.addColumn(columns[index], COLUMN_NAME_PREFIX + (index), String.class.getName(), 20, style, style);
			}
			DynamicReport dynamicReport = drb.setRightMargin(40).setLeftMargin(0).setPrintBackgroundOnOddRows(true)
					.setUseFullPageWidth(true).build();

			DynamicJasperHelper.generateJRXML(dynamicReport, new ClassicLayoutManager(), new HashMap(), ENCODING,
					jrxml.getCanonicalPath());
			return jrxml;
		} catch (Exception e) {
			log.error(e, e);
			throw new ReportGenerationException("Couldn't generate report from", e);
		}
	}

	private static String[] getColumnNames(String URL, String ownerAndReportIds) throws IOException {
		HttpURLConnection connection;
		if (URL.contains("?"))
			connection = (HttpURLConnection) new URL(URL + "&show_header=1&" + ownerAndReportIds).openConnection();
		else
			connection = (HttpURLConnection) new URL(URL + "?show_header=1&" + ownerAndReportIds).openConnection();
		connection.setConnectTimeout(10 * 1000);
		connection.setReadTimeout(10 * 1000);
		BufferedReader br = new BufferedReader(new InputStreamReader(new DataInputStream(connection.getInputStream()), "UTF-8"));
		String columns[] = br.readLine().replaceAll(QUOTE, "").split(String.valueOf(DELIMITER));
		br.close();
		return columns;
	}

	private static File getTemporaryJasper() throws IOException {
		File jrxmlFile = File.createTempFile(TMP_PREFIX, JASPER_SUFFIX);
		jrxmlFile.deleteOnExit();
		FileUtils.forceDeleteOnExit(jrxmlFile);
		tmpFiles.add(jrxmlFile);
		return jrxmlFile;
	}

	private static File getTemporaryJRXML() throws IOException {
		File jrxmlFile = File.createTempFile(TMP_PREFIX, JRXML_SUFFIX);
		jrxmlFile.deleteOnExit();
		FileUtils.forceDeleteOnExit(jrxmlFile);
		tmpFiles.add(jrxmlFile);
		return jrxmlFile;
	}

	public static void main(String[] args) {
		DynamicReportGenerator.configureLog4j();
		if (args.length == 4) {
			try {
				DynamicReportGenerator.props.load(new FileInputStream(new File(args[3])));
			} catch (FileNotFoundException e) {
				log.error("File " + args[3] + " does not exist.", e);
				System.exit(1);
			} catch (IOException e) {
				log.error("Error reading file " + args[3] + ".", e);
				System.exit(1);
			}
		}

		int status = new DynamicReportGenerator().generate(args[0], args[1], args[2]);
		deleteTempFiles();
		System.exit(status);
	}

	public String getParameterSeparator(String url) {
		if (url.contains("?")) {
			return "&";
		} else {
			return "?";
		}
	}

	private void processSubreports(final JasperDesign mainReport, final String ownerAndReportIds) throws Exception {

		final Exception[] exception = new Exception[1];
		JRElementsVisitor.visitReport(mainReport, new JRVisitorSupport() {
			@Override
			public void visitSubreport(JRSubreport subreport) {
				boolean isDynamicReportSubreport = subreport.getExpression().getText() == null;
				if (!isDynamicReportSubreport) {
					return;
				}

				DataSourceExpressionParser dataSourceExpressionParser = new DataSourceExpressionParser(subreport
						.getDataSourceExpression().getText());

				String url = dataSourceExpressionParser.getUrl();
				String newUrl = encodeWhiteSpaces(url) + getParameterSeparator(url) + ownerAndReportIds;
				((JRDesignExpression) subreport.getDataSourceExpression()).setText(dataSourceExpressionParser
						.replaceURLWith(newUrl));

				try {
					File dynamicReportFile = generateDynamicReports(url, ownerAndReportIds);
					if (subreport.getExpression() == null) {
						JRDesignExpression subreportExpression = new JRDesignExpression();
						String fileLocation = (new StringBuilder(DynamicReportGenerator.QUOTE))
								.append(StringUtils.removeEnd(dynamicReportFile.getCanonicalPath(),
										DynamicReportGenerator.JRXML_SUFFIX)).append(DynamicReportGenerator.JASPER_SUFFIX)
								.append(DynamicReportGenerator.QUOTE).toString();
						subreportExpression.setText(fileLocation);
						subreportExpression.setValueClass(String.class);
						((JRDesignSubreport) subreport).setExpression(subreportExpression);
						JasperCompileManager.compileReportToFile(
								dynamicReportFile.getCanonicalPath(),
								(new StringBuilder(String.valueOf(StringUtils.removeEnd(dynamicReportFile.getCanonicalPath(),
										DynamicReportGenerator.JRXML_SUFFIX)))).append(DynamicReportGenerator.JASPER_SUFFIX)
										.toString());
					}
				} catch (Exception e) {
					exception[0] = e;
					return;
				}
			}
		});
		if (exception[0] != null)
			throw exception[0];
	}

	private JRDataSource getJRDataSource(JasperDesign mainReport, String ownerAndReportIds) throws UnsupportedEncodingException,
			JRException {
		for (Object parameter : mainReport.getParametersList()) {
			JRDesignParameter p = (JRDesignParameter) parameter;
			if (p.getName().equals(DATA_URL)) {
				String expression = p.getDefaultValueExpression().getText();
				expression = expression.replaceAll(QUOTE, StringUtils.EMPTY);
				if (expression.contains("?"))
					expression += "&" + ownerAndReportIds;
				else
					expression += "?" + ownerAndReportIds;
				return new JRCsvDataSource(expression, "UTF-8");
			}
		}

		return new JREmptyDataSource();
	}

	public int generate(String inputFile, String outputFile, String ownerAndReportIds) {
		try {
			JasperDesign mainReport = JRXmlLoader.load(inputFile);
			HashMap<String, Object> args = parseArgs(ownerAndReportIds);
			processSubreports(mainReport, ownerAndReportIds);

			File source = DynamicReportGenerator.getTemporaryJRXML();
			JRXmlWriter.writeReport(mainReport, source.getCanonicalPath(), DynamicReportGenerator.ENCODING);
			File destination = getTemporaryJasper();
			JasperCompileManager.compileReportToFile(source.getCanonicalPath(), destination.getCanonicalPath());

			JasperPrint jasperPrint = null;
			if (!args.get(USE_WEBSERVICE).equals("True")) {
				jasperPrint = JasperFillManager.fillReport(destination.getCanonicalPath(), args, getConnection());
			} else {

				jasperPrint = JasperFillManager.fillReport(destination.getCanonicalPath(), new HashMap<String, Object>(),
						getJRDataSource(mainReport, ownerAndReportIds));
			}
			boolean isHtml = outputFile.toLowerCase().endsWith(".html");
			boolean isCsv = outputFile.toLowerCase().endsWith(".csv");
			if (isHtml) {
				JRHtmlExporter exporter = new JRHtmlExporter();
				jasperPrint.setProperty(JRHtmlExporterParameter.PROPERTY_USING_IMAGES_TO_ALIGN, "false");
				exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasperPrint);
				exporter.setParameter(JRExporterParameter.CHARACTER_ENCODING, "UTF-8");
				exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, outputFile);
				exporter.exportReport();
			} else if (isCsv) {
				JRCsvExporter exporter = new JRCsvExporter();
				exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasperPrint);
				exporter.setParameter(JRExporterParameter.CHARACTER_ENCODING, "UTF-8");
				exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, outputFile);
				exporter.exportReport();
			} else {
				JRProperties.setProperty("net.sf.jasperreports.default.pdf.encoding", "UTF-8");
				JasperExportManager.exportReportToPdfFile(jasperPrint, outputFile);
			}

		} catch (Exception e) {
			log.error(e, e);
			return 1;
		}
		return 0;
	}

	private static Connection getConnection() throws ClassNotFoundException, SQLException {
		String driver = "org.postgresql.Driver";
		String connectString = "jdbc:postgresql://" + props.getProperty(DB_HOST) + ":" + props.getProperty(DB_PORT) + "/"
				+ props.getProperty(DB_DATABASE);
		String user = props.getProperty(DB_USER);
		String password = props.getProperty(DB_PASS);

		Class.forName(driver);
		Connection conn = DriverManager.getConnection(connectString, user, password);
		return conn;
	}

	private static HashMap<String, Object> parseArgs(String args) {
		HashMap<String, Object> result = new HashMap<String, Object>();
		for (String pair : args.split("&")) {
			String elems[] = pair.split("=");
			result.put(elems[0], elems[1]);
		}
		return result;
	}
}
