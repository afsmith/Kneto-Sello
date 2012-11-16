package blstream.reports;

import static org.junit.Assert.assertEquals;

import java.io.File;
import java.io.IOException;

import org.apache.commons.io.FilenameUtils;
import org.junit.Ignore;
import org.junit.Test;

@Ignore
public class DynamicReportGeneratorTest {

	private static final int OWNER_ID = 1;

	private static final int REPORT_ID = 1;

	private void generate(String filename) throws IOException {
		String filePath = DynamicReportGeneratorTest.class.getClassLoader().getResource(filename).getFile();
		int status = new DynamicReportGenerator().generate(filePath, File.createTempFile(FilenameUtils.getBaseName(filePath), ".pdf")
				.getCanonicalPath(), Integer.valueOf(OWNER_ID).toString());
		assertEquals(0, status);
	}

	@Test
	public void testFilesNumberGroupId() throws IOException {
		generate("files_number_group_id.jrxml");
	}

	@Test
	public void testFilesNumberUserId() throws IOException {
		generate("files_number_user_id.jrxml");
	}

	@Test
	public void testModulesUsageCourseId() throws IOException {
		generate("modules_usage_course_id.jrxml");
	}

	@Test
	public void testModulesUsageGroupId() throws IOException {
		generate("modules_usage_group_id.jrxml");
	}

	@Test
	public void testModulesUsageUserId() throws IOException {
		generate("modules_usage_user_id.jrxml");
	}

	@Test
	public void testNumberOfAdminModules() throws IOException {
		generate("number_of_admin_modules.jrxml");
	}

	@Test
	public void testNumberOfAdminModulesGroupId() throws IOException {
		generate("number_of_admin_modules_group_id.jrxml");
	}

	@Test
	public void testNumberOfPublishedModules() throws IOException {
		generate("number_of_published_modules.jrxml");
	}

	@Test
	public void testNumberOfPublishedModulesGroupId() throws IOException {
		generate("number_of_published_modules_group_id.jrxml");
	}

	@Test
	public void testTotalTimeCourseId() throws IOException {
		generate("total_time_course_id.jrxml");
	}

	@Test
	public void testTotalTimeGroupId() throws IOException {
		generate("total_time_group_id.jrxml");
	}

	@Test
	public void testTotalTimeUserId() throws IOException {
		generate("total_time_user_id.jrxml");
	}

	@Test
	public void testTrackingGroupId() throws IOException {
		generate("tracking_group_id.jrxml");
	}

	@Test
	public void testUserProgressGroupId() throws IOException {
		generate("user_progress_group_id.jrxml");
	}

	@Test
	public void testUserProgressUserId() throws IOException {
		generate("user_progress_user_id.jrxml");
	}

	@Test
	public void testUserProgressWithScormGroupId() throws IOException {
		generate("user_progress_with_scorm_group_id.jrxml");
	}

	@Test
	public void testUserProgressWithScormUserId() throws IOException {
		generate("user_progress_with_scorm_user_id.jrxml");
	}

	@Test
	public void testUsersPerModule() throws IOException {
		generate("users_per_module.jrxml");
	}

	@Test
	public void testUsersPerModuleGroupId() throws IOException {
		generate("users_per_module_group_id.jrxml");
	}
}
