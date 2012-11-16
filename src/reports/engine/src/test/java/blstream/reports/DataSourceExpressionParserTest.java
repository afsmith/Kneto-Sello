package blstream.reports;

import org.junit.Assert;
import org.junit.Test;

public class DataSourceExpressionParserTest {

	private String SIMPLE = "new net.sf.jasperreports.engine.data.JRCsvDataSource(net.sf.jasperreports.engine.util.JRLoader.getInputStreamFromLocation(\"http://127.0.0.1:81/tracking/report_tracking\"))";

	private String COMPLEX = "new net.sf.jasperreports.engine.data.JRCsvDataSource(net.sf.jasperreports.engine.util.JRLoader.getInputStreamFromLocation(\"http://127.0.0.1:81/tracking/report_tracking\"))";

	private String COMPLEX_WITH_PARAMS = "new net.sf.jasperreports.engine.data.JRCsvDataSource(net.sf.jasperreports.engine.util.JRLoader.getInputStreamFromLocation(\"http://127.0.0.1:81/tracking/user_progress?show_scorm=1&asd=ss\"))";

	@Test
	public void testGetUrlFromExpressionWithoutCharset() {
		DataSourceExpressionParser dsep = new DataSourceExpressionParser(SIMPLE);

		Assert.assertEquals(dsep.getUrl(), "http://127.0.0.1:81/tracking/report_tracking");
	}

	@Test
	public void testGetUrlFromExpressionWithCharset() {
		DataSourceExpressionParser dsep = new DataSourceExpressionParser(COMPLEX);
		Assert.assertEquals("http://127.0.0.1:81/tracking/report_tracking", dsep.getUrl());
	}

	@Test
	public void testReplaceUrlInExpresionWithoutCharset() {
		DataSourceExpressionParser dsep = new DataSourceExpressionParser(SIMPLE);
		Assert.assertEquals(SIMPLE.replace("http://127.0.0.1:81/tracking/report_tracking", "NEW_URL"),
				dsep.replaceURLWith("NEW_URL"));
	}

	@Test
	public void testReplaceUrlInExpresionWithCharset() {
		DataSourceExpressionParser dsep = new DataSourceExpressionParser(COMPLEX);
		Assert.assertEquals(COMPLEX.replace("http://127.0.0.1:81/tracking/report_tracking", "NEW_URL"),
				dsep.replaceURLWith("NEW_URL"));
	}

	@Test
	public void testUrlWithParams() {
		DataSourceExpressionParser dsep = new DataSourceExpressionParser(COMPLEX_WITH_PARAMS);
		Assert.assertEquals("http://127.0.0.1:81/tracking/user_progress?show_scorm=1&asd=ss", dsep.getUrl());
	}
}
